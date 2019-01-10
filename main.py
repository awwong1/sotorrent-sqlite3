#!/usr/bin/env python

import os
import sqlite3
from sqlite3 import Error
from xml.etree.ElementTree import iterparse
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
db_file_name = "sotorrent18_12.sqlite3"
db_file = os.path.join(script_dir, db_file_name)


def create_database(conn):
    """sqlite version of 1_create_database.sql"""

    # PostType
    sql_create_posttype = """
        CREATE TABLE PostType (
            Id TINYINT NOT NULL,
            Type VARCHAR(50) NOT NULL,
            PRIMARY KEY(Id)
        );"""
    sql_posttypes = [
        (1, 'Question'),
        (2, 'Answer'),
        (3, 'Wiki'),
        (4, 'TagWikiExcerpt'),
        (5, 'TagWiki'),
        (6, 'ModeratorNomination'),
        (7, 'WikiPlaceholder'),
        (8, 'PrivilegeWiki'),
        (99, 'Comment')
    ]
    sql_insert_posttype = "INSERT INTO PostType VALUES (?, ?);"

    # PostHistoryType
    sql_create_posthistorytype = """
        CREATE TABLE PostHistoryType (
            Id TINYINT NOT NULL,
            Type VARCHAR(50) NOT NULL,
            PRIMARY KEY(Id)
        );"""
    sql_posthistorytypes = [
        (1, 'Initial Title'),
        (2, 'Initial Body'),
        (3, 'Initial Tags'),
        (4, 'Edit Title'),
        (5, 'Edit Body'),
        (6, 'Edit Tags'),
        (7, 'Rollback Title'),
        (8, 'Rollback Body'),
        (9, 'Rollback Tags'),
        (10, 'Post Closed'),
        (11, 'Post Reopened'),
        (12, 'Post Deleted'),
        (13, 'Post Undeleted'),
        (14, 'Post Locked'),
        (15, 'Post Unlocked'),
        (16, 'Community Owned'),
        (17, 'Post Migrated'),
        (18, 'Question Merged'),
        (19, 'Question Protected'),
        (20, 'Question Unprotected'),
        (22, 'Question Unmerged'),
        (24, 'Suggested Edit Applied'),
        (25, 'Post Tweeted'),
        (31, 'Discussion moved to chat'),
        (33, 'Post Notice Added'),
        (34, 'Post Notice Removed'),
        (35, 'Post Migrated Away'),
        (36, 'Post Migrated Here'),
        (37, 'Post Merge Source'),
        (38, 'Post Merge Destination'),
        (50, 'CommunityBump')
    ]
    sql_insert_posthistorytype = "INSERT INTO PostHistoryType VALUES (?, ?);"

    # rest of the data tables
    sql_create_users = """
        CREATE TABLE Users (
            Id INT NOT NULL,
            Reputation INT NOT NULL,
            CreationDate DATETIME,
            DisplayName VARCHAR(40),
            LastAccessDate DATETIME,
            WebsiteUrl VARCHAR(200),
            Location VARCHAR(100),
            ProfileImageUrl VARCHAR(200),
            AboutMe TEXT,
            Views INT DEFAULT 0,
            UpVotes INT,
            DownVotes INT,
            Age INT,
            AccountId INT,
            EmailHash VARCHAR(32),
            PRIMARY KEY (Id)
        );"""
    sql_create_badges = """
        CREATE TABLE Badges (
            Id INT NOT NULL,
            UserId INT NOT NULL,
            Name VARCHAR(50),
            Date DATETIME,
            Class TINYINT,
            TagBased TINYINT(1),
            PRIMARY KEY (Id),
            FOREIGN KEY (UserId) REFERENCES Users(Id)
        );"""
    sql_create_posts = """
        CREATE TABLE Posts (
            Id INT NOT NULL,
            PostTypeId TINYINT,
            AcceptedAnswerId INT,
            ParentId INT,
            CreationDate DATETIME,
            DeletionDate DATETIME,
            Score INT,
            ViewCount INT,
            Body TEXT,
            OwnerUserId INT,
            OwnerDisplayName VARCHAR(40),
            LastEditorUserId INT,
            LastEditorDisplayName VARCHAR(40),
            LastEditDate DATETIME,
            LastActivityDate DATETIME,
            Title VARCHAR(250),
            Tags VARCHAR(150),
            AnswerCount INT DEFAULT 0,
            CommentCount INT DEFAULT 0,
            FavoriteCount INT DEFAULT 0,
            ClosedDate DATETIME,
            CommunityOwnedDate DATETIME,
            PRIMARY KEY (Id),
            FOREIGN KEY (AcceptedAnswerId) REFERENCES Posts(Id),
            FOREIGN KEY (ParentId) REFERENCES Posts(Id),
            FOREIGN KEY (PostTypeId) REFERENCES PostType(Id)
        );"""
    sql_create_comments = """
        CREATE TABLE Comments (
            Id INT NOT NULL,
            PostId INT NOT NULL,
            Score INT NOT NULL DEFAULT 0,
            Text TEXT,
            CreationDate DATETIME NOT NULL,
            UserDisplayName VARCHAR(40),
            UserId INT,
            PRIMARY KEY (Id),
            FOREIGN KEY (PostId) REFERENCES Posts(Id)
        );"""
    sql_create_posthistory = """
        CREATE TABLE PostHistory (
            Id INT NOT NULL,
            PostHistoryTypeId TINYINT NOT NULL,
            PostId INT NOT NULL,
            RevisionGUID VARCHAR(64),
            CreationDate DATETIME,
            UserId INT,
            UserDisplayName VARCHAR(40),
            Comment TEXT,
            Text MEDIUMTEXT,
            PRIMARY KEY (Id),
            FOREIGN KEY (PostId) REFERENCES Posts(Id),
            FOREIGN KEY (PostHistoryTypeId) REFERENCES PostHistoryType(Id)
        );"""
    sql_create_postlinks = """
        CREATE TABLE PostLinks (
            Id INT NOT NULL,
            CreationDate DATETIME,
            PostId INT NOT NULL,
            RelatedPostId INT NOT NULL,
            LinkTypeId TINYINT,
            PRIMARY KEY (Id),
            FOREIGN KEY (PostId) REFERENCES Posts(Id),
            FOREIGN KEY (RelatedPostId) REFERENCES Posts(Id)
        );"""
    sql_create_tags = """
        CREATE TABLE Tags (
            Id INT NOT NULL,
            TagName VARCHAR(64),
            Count INT,
            ExcerptPostId INT,
            WikiPostId INT,
            PRIMARY KEY(Id)
        );"""
    sql_create_votes = """
        CREATE TABLE Votes (
            Id INT NOT NULL,
            PostId INT NOT NULL,
            VoteTypeId TINYINT,
            UserId INT,
            CreationDate DATETIME,
            BountyAmount INT,
            PRIMARY KEY (Id),
            FOREIGN KEY (PostId) REFERENCES Posts(Id),
            FOREIGN KEY (UserId) REFERENCES Users(Id)
        );"""

    c = conn.cursor()

    # PostType
    c.execute(sql_create_posttype)
    c.executemany(sql_insert_posttype, sql_posttypes)

    # PostHistoryType
    c.execute(sql_create_posthistorytype)
    c.executemany(sql_insert_posthistorytype, sql_posthistorytypes)

    # Data Tables
    c.execute(sql_create_users)
    c.execute(sql_create_badges)
    c.execute(sql_create_posts)
    c.execute(sql_create_comments)
    c.execute(sql_create_posthistory)
    c.execute(sql_create_postlinks)
    c.execute(sql_create_tags)
    c.execute(sql_create_votes)

    conn.commit()
    print("1_create_database done")


def load_so_from_xml(conn):
    """sqlite version of 2_load_so_from_xml.sql"""
    c = conn.cursor()

    table = "Users"

    # load from xml
    xml_filepath = os.path.join(script_dir, "{}.xml".format(table))
    context = iterparse(xml_filepath, events=("end",))

    t_start = datetime.now()
    c.execute("PRAGMA foreign_keys = OFF;")
    commit_block = 1024 * 1024 # arbitrary
    counter = 0
    commit_counter = 0
    for _, elm in context:
        if elm.tag != "row":
            continue
        columns = elm.keys()
        values = [elm.get(column) for column in columns]
        sql_insert = "INSERT INTO {table} ({columns}) VALUES ({q_s})".format(
            table="Users",
            columns=", ".join(columns),
            q_s=", ".join(["?" for _ in range(0, len(columns))])
        )
        # print(sql_insert, [values])
        c.execute(sql_insert, values)
        counter += 1
        if counter % commit_block == 0:
            conn.commit() # must commit or all changes still in memory
            commit_counter += 1
            print("\tcommit no {}, elapsed: {}".format(
                commit_counter, datetime.now() - t_start))

    c.execute("PRAGMA foreign_keys = ON;")
    conn.commit()
    print("\t{} took {} ({} rows)".format(table, datetime.now() - t_start, counter))



def main():
    try:
        conn = sqlite3.connect(db_file)
        create_database(conn)
        load_so_from_xml(conn)
    except Error as e:
        print(e)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

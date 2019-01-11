#!/usr/bin/env python3

import os
from csv import reader
from sqlite3 import connect, Error
from xml.etree.ElementTree import iterparse
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))
db_file_name = "sotorrent18_12.sqlite3"
db_file = os.path.join(script_dir, db_file_name)
commit_block = 1024  # arbitrary


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

    tables = ["Users", "Badges", "Posts", "Comments",
              "PostHistory", "PostLinks", "Tags", "Votes"]

    for table in tables:
        # load from xml
        xml_filepath = os.path.join(script_dir, "{}.xml".format(table))
        context = iterparse(xml_filepath, events=("end",))

        t_start = datetime.now()
        print("\tStarting {} at {}".format(table, t_start))
        c.execute("PRAGMA foreign_keys = OFF;")
        counter = 0
        commit_counter = 0
        for _, elm in context:
            if elm.tag != "row":
                continue
            columns = elm.keys()
            values = [elm.get(column) for column in columns]
            sql_insert = "INSERT INTO {table} ({columns}) VALUES ({q_s})".format(
                table=table,
                columns=", ".join(columns),
                q_s=", ".join(["?" for _ in range(0, len(columns))])
            )
            # print(sql_insert, [values])
            c.execute(sql_insert, values)
            counter += 1
            if counter % commit_block == 0:
                conn.commit()  # must commit or all changes still in memory
                commit_counter += 1
                print("\tcommit no {}, elapsed: {}".format(
                    commit_counter, datetime.now() - t_start))

        c.execute("PRAGMA foreign_keys = ON;")
        conn.commit()
        print("\t{} took {} ({} rows)".format(
            table, datetime.now() - t_start, counter))

    print("2_load_so_from_xml done")


def create_indicies(conn):
    """3_create_indicies.sql"""
    c = conn.cursor()
    c.execute("CREATE INDEX comments_index_1 ON Comments(UserId);")
    c.execute("CREATE INDEX comments_index_2 ON Comments(UserDisplayName);")

    c.execute("CREATE INDEX post_history_index_1 ON PostHistory(UserId);")
    c.execute("CREATE INDEX post_history_index_2 ON PostHistory(UserDisplayName);")

    c.execute("CREATE INDEX posts_index_1 ON Posts(OwnerUserId);")
    c.execute("CREATE INDEX posts_index_2 ON Posts(LastEditorUserId);")
    c.execute("CREATE INDEX posts_index_3 ON Posts(OwnerDisplayName);")

    c.execute("CREATE INDEX users_index_1 ON Users(DisplayName);")
    conn.commit()
    print("3_create_indicies done")


def create_sotorrent_tables(conn):
    """4_create_sotorrent_tables.sql"""

    sql_create_postblocktype = """
        CREATE TABLE PostBlockType (
            Id TINYINT NOT NULL,
            Type VARCHAR(50) NOT NULL,
            PRIMARY KEY(Id)
        );"""
    sql_postblocktypes = [(1, 'TextBlock'), (2, 'CodeBlock')]
    sql_insert_postblocktype = "INSERT INTO PostBlockType VALUES(?,?);"

    sql_create_postblockdiffoperation = """
        CREATE TABLE PostBlockDiffOperation (
            Id TINYINT NOT NULL,
            Name VARCHAR(50) NOT NULL,
            PRIMARY KEY(Id)
        );"""
    sql_postblockdiffoperations = [(-1, 'DELETE'), (0, 'EQUAL'), (1, 'INSERT')]
    sql_insert_postblockdiffoperations = "INSERT INTO PostBlockDiffOperation VALUES(?, ?);"

    sql_create_postversion = """
        CREATE TABLE PostVersion (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            PostId INT NOT NULL,
            PostTypeId TINYINT NOT NULL,
            PostHistoryId INT NOT NULL,
            PostHistoryTypeId TINYINT NOT NULL,
            CreationDate DATETIME NOT NULL,
            PredPostHistoryId INT DEFAULT NULL,
            SuccPostHistoryId INT DEFAULT NULL,
            UNIQUE(PostHistoryId, PredPostHistoryId, SuccPostHistoryId),
            FOREIGN KEY(PostId) REFERENCES Posts(Id),
            FOREIGN KEY(PostHistoryId) REFERENCES PostHistory(Id),
            FOREIGN KEY(PostTypeId) REFERENCES PostType(Id),
            FOREIGN KEY(PostHistoryTypeId) REFERENCES PostHistoryType(Id),
            FOREIGN KEY(PredPostHistoryId) REFERENCES PostHistory(Id),
            FOREIGN KEY(SuccPostHistoryId) REFERENCES PostHistory(Id)
        );"""

    sql_create_postblockversion = """
        CREATE TABLE PostBlockVersion (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            PostBlockTypeId TINYINT NOT NULL,
            PostId INT NOT NULL,
            PostHistoryId INT NOT NULL,
            LocalId INT NOT NULL,
            PredPostBlockVersionId INT DEFAULT NULL,
            PredPostHistoryId INT DEFAULT NULL,
            PredLocalId INT DEFAULT NULL,
            RootPostBlockVersionId INT DEFAULT NULL,
            RootPostHistoryId INT DEFAULT NULL,
            RootLocalId INT DEFAULT NULL,
            PredEqual BOOLEAN DEFAULT NULL,
            PredSimilarity DOUBLE DEFAULT NULL,
            PredCount INT DEFAULT NULL,
            SuccCount INT DEFAULT NULL,
            Length INT NOT NULL,
            LineCount INT NOT NULL,
            Content TEXT NOT NULL,
            UNIQUE(PostHistoryId, PostBlockTypeId, LocalId),
            FOREIGN KEY(PostBlockTypeId) REFERENCES PostBlockType(Id),
            FOREIGN KEY(PostId) REFERENCES Posts(Id),
            FOREIGN KEY(PostHistoryId) REFERENCES PostHistory(Id),
            FOREIGN KEY(PredPostBlockVersionId) REFERENCES PostBlockVersion(Id),
            FOREIGN KEY(PredPostHistoryId) REFERENCES PostHistory(Id),
            FOREIGN KEY(RootPostBlockVersionId) REFERENCES PostBlockVersion(Id),
            FOREIGN KEY(RootPostHistoryId) REFERENCES PostHistory(Id)
        );"""

    sql_create_postblockdiff = """
        CREATE TABLE PostBlockDiff (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            PostId INT NOT NULL,
            PostHistoryId INT NOT NULL,
            LocalId INT NOT NULL,
            PostBlockVersionId INT NOT NULL,
            PredPostHistoryId INT NOT NULL,
            PredLocalId INT NOT NULL,
            PredPostBlockVersionId INT NOT NULL,
            PostBlockDiffOperationId TINYINT NOT NULL,
            Text TEXT NOT NULL,
            FOREIGN KEY(PostId) REFERENCES Posts(Id),
            FOREIGN KEY(PostHistoryId) REFERENCES PostHistory(Id),
            FOREIGN KEY(PredPostHistoryId) REFERENCES PostHistory(Id),
            FOREIGN KEY(PostBlockDiffOperationId) REFERENCES PostBlockDiffOperation(Id),
            FOREIGN KEY(PostBlockVersionId) REFERENCES PostBlockVersion(Id),
            FOREIGN KEY(PredPostBlockVersionId) REFERENCES PostBlockVersion(Id)
        );"""

    sql_create_postversionurl = """
        CREATE TABLE PostVersionUrl (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            PostId INT NOT NULL,
            PostHistoryId INT NOT NULL,
            PostBlockVersionId INT NOT NULL,
            LinkType VARCHAR(32) NOT NULL,
            LinkPosition VARCHAR(32) NOT NULL,
            LinkAnchor TEXT DEFAULT NULL,
            Protocol TEXT NOT NULL,
            RootDomain TEXT NOT NULL,
            CompleteDomain TEXT NOT NULL,
            Path TEXT DEFAULT NULL,
            Query TEXT DEFAULT NULL,
            FragmentIdentifier TEXT DEFAULT NULL,
            Url TEXT NOT NULL,
            FullMatch TEXT NOT NULL,
            FOREIGN KEY(PostId) REFERENCES Posts(Id),
            FOREIGN KEY(PostHistoryId) REFERENCES PostHistory(Id),
            FOREIGN KEY(PostBlockVersionId) REFERENCES PostBlockVersion(Id)
        );"""
    sql_create_commenturl = """
        CREATE TABLE CommentUrl (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            PostId INT NOT NULL,
            CommentId INT NOT NULL,
            LinkType VARCHAR(32) NOT NULL,
            LinkPosition VARCHAR(32) NOT NULL,
            LinkAnchor TEXT DEFAULT NULL,
            Protocol TEXT NOT NULL,
            RootDomain TEXT NOT NULL,
            CompleteDomain TEXT NOT NULL,
            Path TEXT DEFAULT NULL,
            Query TEXT DEFAULT NULL,
            FragmentIdentifier TEXT DEFAULT NULL,
            Url TEXT NOT NULL,
            FullMatch TEXT NOT NULL,
            FOREIGN KEY(CommentId) REFERENCES Comments(Id)
        );"""
    sql_create_postreferencegh = """
        CREATE TABLE PostReferenceGH (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            FileId VARCHAR(40) NOT NULL,
            Repo VARCHAR(255) NOT NULL,
            RepoOwner VARCHAR(255) NOT NULL,
            RepoName VARCHAR(255) NOT NULL,
            Branch VARCHAR(255) NOT NULL,
            Path TEXT NOT NULL,
            FileExt VARCHAR(255) NOT NULL,
            Size INT NOT NULL,
            Copies INT NOT NULL,
            PostId INT NOT NULL,
            PostTypeId TINYINT NOT NULL,
            CommentId INT DEFAULT NULL,
            SOUrl TEXT NOT NULL,
            GHUrl TEXT NOT NULL,
            FOREIGN KEY(PostId) REFERENCES Posts(Id),
            FOREIGN KEY(PostTypeId) REFERENCES PostType(Id)
        );"""
    sql_create_titleversion = """
        CREATE TABLE TitleVersion (
            Id INTEGER PRIMARY KEY AUTOINCREMENT,
            PostId INT NOT NULL,
            PostTypeId TINYINT NOT NULL,
            PostHistoryId INT NOT NULL,
            PostHistoryTypeId TINYINT NOT NULL,
            CreationDate DATETIME NOT NULL,
            Title TEXT NOT NULL,
            PredPostHistoryId INT DEFAULT NULL,
            PredEditDistance INT DEFAULT NULL,
            SuccPostHistoryId INT DEFAULT NULL,
            SuccEditDistance INT DEFAULT NULL,
            UNIQUE(PostHistoryId, PredPostHistoryId, SuccPostHistoryId),
            FOREIGN KEY(PostId) REFERENCES Posts(Id),
            FOREIGN KEY(PostTypeId) REFERENCES PostType(Id),
            FOREIGN KEY(PostHistoryId) REFERENCES PostHistory(Id),
            FOREIGN KEY(PostHistoryTypeId) REFERENCES PostHistoryType(Id),
            FOREIGN KEY(PredPostHistoryId) REFERENCES PostHistory(Id),
            FOREIGN KEY(SuccPostHistoryId) REFERENCES PostHistory(Id)
        );"""
    sql_create_ghmatches = """
        CREATE TABLE GHMatches (
            FileId VARCHAR(40) NOT NULL,
            MatchedLine LONGTEXT NOT NULL
        );"""

    c = conn.cursor()
    # PostBlockType
    c.execute(sql_create_postblocktype)
    c.executemany(sql_insert_postblocktype, sql_postblocktypes)

    # PostBlockDiffOperation
    c.execute(sql_create_postblockdiffoperation)
    c.executemany(sql_insert_postblockdiffoperations,
                  sql_postblockdiffoperations)

    # SO Torrent data tables
    c.execute(sql_create_postversion)
    c.execute(sql_create_postblockversion)
    c.execute(sql_create_postblockdiff)
    c.execute(sql_create_postversionurl)
    c.execute(sql_create_commenturl)
    c.execute(sql_create_postreferencegh)
    c.execute(sql_create_titleversion)
    c.execute(sql_create_ghmatches)

    conn.commit()
    print("4_create_sotorrent_tables done")


def load_sotorrent(conn):
    """sqlite version of 6_load_sotorrent.sql"""
    c = conn.cursor()

    # PostBlockDiff
    csv_filepath = os.path.join(script_dir, "PostBlockDiff.csv")
    with open(csv_filepath) as csvfile:
        t_start = datetime.now()
        c.execute("PRAGMA foreign_keys = OFF;")
        print("\tStarting PostBlockDiff at {}".format(t_start))
        csv_reader = reader(csvfile, delimiter=',', quotechar='"')
        counter = 0
        commit_counter = 0
        for row in csv_reader:
            (Id, PostId, PostHistoryId, LocalId, PostBlockVersionId, PredPostHistoryId,
             PredLocalId, PredPostBlockVersionId, PostBlockDiffOperationId, Text) = row
            Text = Text.replace('&#xD;&#xA;', '\n')
            c.execute("""
                INSERT INTO PostBlockDiff
                    (Id, PostId, PostHistoryId, LocalId, PostBlockVersionId, PredPostHistoryId,
                    PredLocalId, PredPostBlockVersionId, PostBlockDiffOperationId, Text)
                    VALUES (?,?,?,?,?,?,?,?,?,?)
                """, (Id, PostId, PostHistoryId, LocalId, PostBlockVersionId, PredPostHistoryId,
                      PredLocalId, PredPostBlockVersionId, PostBlockDiffOperationId, Text))
            counter += 1
            if counter % commit_block == 0:
                conn.commit()  # must commit or all changes still in memory
                commit_counter += 1
                print("\tcommit no {}, elapsed: {}".format(
                    commit_counter, datetime.now() - t_start))
        print("\tPostBlockDiff took {} ({} rows)".format(
            datetime.now() - t_start, counter))
        c.execute("PRAGMA foreign_keys = ON;")
        conn.commit()

    # PostVersion
    csv_filepath = os.path.join(script_dir, "PostVersion.csv")
    with open(csv_filepath) as csvfile:
        t_start = datetime.now()
        c.execute("PRAGMA foreign_keys = OFF;")
        print("\tStarting PostVersion at {}".format(t_start))
        csv_reader = reader(csvfile, delimiter=',', quotechar='"')
        counter = 0
        commit_counter = 0
        for row in csv_reader:
            (Id, PostId, PostTypeId, PostHistoryId, PostHistoryTypeId,
             CreationDate, PredPostHistoryId, SuccPostHistoryId) = row
            if not PredPostHistoryId:
                PredPostHistoryId = None
            if not SuccPostHistoryId:
                SuccPostHistoryId = None
            c.execute("""
                INSERT INTO PostVersion
                    (Id, PostId, PostTypeId, PostHistoryId, PostHistoryTypeId,
                    CreationDate, PredPostHistoryId, SuccPostHistoryId)
                    VALUES (?,?,?,?,?,?,?,?)
                """, (Id, PostId, PostTypeId, PostHistoryId, PostHistoryTypeId,
                      CreationDate, PredPostHistoryId, SuccPostHistoryId))
            counter += 1
            if counter % commit_block == 0:
                conn.commit()  # must commit or all changes still in memory
                commit_counter += 1
                print("\tcommit no {}, elapsed: {}".format(
                    commit_counter, datetime.now() - t_start))
        print("\tPostVersion took {} ({} rows)".format(
            datetime.now() - t_start, counter))
        c.execute("PRAGMA foreign_keys = ON;")
        conn.commit()

    # PostBlockVersion
    csv_filepath = os.path.join(script_dir, "PostBlockVersion.csv")
    with open(csv_filepath) as csvfile:
        t_start = datetime.now()
        print("\tStarting PostBlockVersion at {}".format(t_start))
        c.execute("PRAGMA foreign_keys = OFF;")
        csv_reader = reader(csvfile, delimiter=',', quotechar='"')
        counter = 0
        commit_counter = 0
        for row in csv_reader:
            (Id, PostBlockTypeId, PostId, PostHistoryId, LocalId, PredPostBlockVersionId, PredPostHistoryId, PredLocalId, RootPostBlockVersionId,
             RootPostHistoryId, RootLocalId, PredEqual, PredSimilarity, PredCount, SuccCount, Length, LineCount, Content) = row
            Content = Content.replace('&#xD;&#xA;', '\n')
            if not PredPostBlockVersionId:
                PredPostBlockVersionId = None
            if not PredPostHistoryId:
                PredPostHistoryId = None
            if not PredLocalId:
                PredLocalId = None
            if not RootPostBlockVersionId:
                RootPostBlockVersionId = None
            if not RootPostHistoryId:
                RootPostHistoryId = None
            if not RootLocalId:
                RootLocalId = None
            if not PredEqual:
                PredEqual = None
            if not PredSimilarity:
                PredSimilarity = None
            if not PredCount:
                PredCount = None
            if not SuccCount:
                SuccCount = None
            c.execute("""
                INSERT INTO PostBlockVersion
                    (Id, PostBlockTypeId, PostId, PostHistoryId, LocalId, PredPostBlockVersionId, PredPostHistoryId, PredLocalId, RootPostBlockVersionId,
                    RootPostHistoryId, RootLocalId, PredEqual, PredSimilarity, PredCount, SuccCount, Length, LineCount, Content)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (Id, PostBlockTypeId, PostId, PostHistoryId, LocalId, PredPostBlockVersionId, PredPostHistoryId, PredLocalId, RootPostBlockVersionId,
                      RootPostHistoryId, RootLocalId, PredEqual, PredSimilarity, PredCount, SuccCount, Length, LineCount, Content))
            counter += 1
            if counter % commit_block == 0:
                conn.commit()  # must commit or all changes still in memory
                commit_counter += 1
                print("\tcommit no {}, elapsed: {}".format(
                    commit_counter, datetime.now() - t_start))
        print("\tPostBlockVersion took {} ({} rows)".format(
            datetime.now() - t_start, counter))
        c.execute("PRAGMA foreign_keys = ON;")
        conn.commit()

    # PostVersionUrl
    csv_filepath = os.path.join(script_dir, "PostVersionUrl.csv")
    with open(csv_filepath) as csvfile:
        t_start = datetime.now()
        print("\tStarting PostVersionUrl at {}".format(t_start))
        c.execute("PRAGMA foreign_keys = OFF;")
        csv_reader = reader(csvfile, delimiter=',', quotechar='"')
        counter = 0
        commit_counter = 0
        for row in csv_reader:
            (Id, PostId, PostHistoryId, PostBlockVersionId, LinkType, LinkPosition, LinkAnchor,
             Protocol, RootDomain, CompleteDomain, Path, Query, FragmentIdentifier, Url, FullMatch) = row
            LinkAnchor = LinkAnchor.replace('&#xD;&#xA;', '\n')
            if not LinkAnchor:
                LinkAnchor = None
            if not Path:
                Path = None
            if not Query:
                Query = None
            if not FragmentIdentifier:
                FragmentIdentifier = None
            FullMatch = FullMatch.replace('&#xD;&#xA;', '\n')
            c.execute("""
                INSERT INTO PostVersionUrl
                    (Id, PostId, PostHistoryId, PostBlockVersionId, LinkType, LinkPosition, LinkAnchor,
                     Protocol, RootDomain, CompleteDomain, Path, Query, FragmentIdentifier, Url, FullMatch)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (Id, PostId, PostHistoryId, PostBlockVersionId, LinkType, LinkPosition, LinkAnchor,
                      Protocol, RootDomain, CompleteDomain, Path, Query, FragmentIdentifier, Url, FullMatch))
            counter += 1
            if counter % commit_block == 0:
                conn.commit()  # must commit or all changes still in memory
                commit_counter += 1
                print("\tcommit no {}, elapsed: {}".format(
                    commit_counter, datetime.now() - t_start))
        print("\tPostVersionUrl took {} ({} rows)".format(
            datetime.now() - t_start, counter))
        c.execute("PRAGMA foreign_keys = ON;")
        conn.commit()

    # CommentUrl
    csv_filepath = os.path.join(script_dir, "CommentUrl.csv")
    with open(csv_filepath) as csvfile:
        t_start = datetime.now()
        print("\tStarting CommentUrl at {}".format(t_start))
        c.execute("PRAGMA foreign_keys = OFF;")
        csv_reader = reader(csvfile, delimiter=',', quotechar='"')
        counter = 0
        commit_counter = 0
        for row in csv_reader:
            (Id, PostId, CommentId, LinkType, LinkPosition, LinkAnchor, Protocol, RootDomain,
             CompleteDomain, Path, Query, FragmentIdentifier, Url, FullMatch) = row
            LinkAnchor = LinkAnchor.replace('&#xD;&#xA;', '\n')
            if not LinkAnchor:
                LinkAnchor = None
            if not Path:
                Path = None
            if not Query:
                Query = None
            if not FragmentIdentifier:
                FragmentIdentifier = None
            FullMatch = FullMatch.replace('&#xD;&#xA;', '\n')
            c.execute("""
                INSERT INTO CommentUrl
                    (Id, PostId, CommentId, LinkType, LinkPosition, LinkAnchor, Protocol, RootDomain,
                     CompleteDomain, Path, Query, FragmentIdentifier, Url, FullMatch)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (Id, PostId, CommentId, LinkType, LinkPosition, LinkAnchor, Protocol, RootDomain,
                      CompleteDomain, Path, Query, FragmentIdentifier, Url, FullMatch))
            counter += 1
            if counter % commit_block == 0:
                conn.commit()  # must commit or all changes still in memory
                commit_counter += 1
                print("\tcommit no {}, elapsed: {}".format(
                    commit_counter, datetime.now() - t_start))
        print("\tCommentUrl took {} ({} rows)".format(
            datetime.now() - t_start, counter))
        c.execute("PRAGMA foreign_keys = ON;")
        conn.commit()

    # TitleVersion
    csv_filepath = os.path.join(script_dir, "TitleVersion.csv")
    with open(csv_filepath) as csvfile:
        t_start = datetime.now()
        print("\tStarting TitleVersion at {}".format(t_start))
        c.execute("PRAGMA foreign_keys = OFF;")
        csv_reader = reader(csvfile, delimiter=',', quotechar='"')
        counter = 0
        commit_counter = 0
        for row in csv_reader:
            (Id, PostId, PostTypeId, PostHistoryId, PostHistoryTypeId, CreationDate, Title,
             PredPostHistoryId, PredEditDistance, SuccPostHistoryId, SuccEditDistance) = row
            if not PredPostHistoryId:
                PredPostHistoryId = None
            if not PredEditDistance:
                PredEditDistance = None
            if not SuccPostHistoryId:
                SuccPostHistoryId = None
            if not SuccEditDistance:
                SuccEditDistance = None
            c.execute("""
                INSERT INTO TitleVersion
                    (Id, PostId, PostTypeId, PostHistoryId, PostHistoryTypeId, CreationDate, Title,
                     PredPostHistoryId, PredEditDistance, SuccPostHistoryId, SuccEditDistance)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)
                """, (Id, PostId, PostTypeId, PostHistoryId, PostHistoryTypeId, CreationDate, Title,
                      PredPostHistoryId, PredEditDistance, SuccPostHistoryId, SuccEditDistance))
            counter += 1
            if counter % commit_block == 0:
                conn.commit()  # must commit or all changes still in memory
                commit_counter += 1
                print("\tcommit no {}, elapsed: {}".format(
                    commit_counter, datetime.now() - t_start))
        print("\tTitleVersion took {} ({} rows)".format(
            datetime.now() - t_start, counter))
        c.execute("PRAGMA foreign_keys = ON;")
        conn.commit()
    print("6_load_sotorrent done")


def load_postreferencegh(conn):
    """7_load_postreferencegh.sql"""
    c = conn.cursor()

    csv_filepath = os.path.join(script_dir, "PostReferenceGH.csv")
    with open(csv_filepath) as csvfile:
        t_start = datetime.now()
        print("\tStarting PostReferenceGH at {}".format(t_start))
        c.execute("PRAGMA foreign_keys = OFF;")
        csv_reader = reader(csvfile, delimiter=',', quotechar='"')
        counter = 0
        commit_counter = 0
        skipped_one = False
        for row in csv_reader:
            if not skipped_one:
                skipped_one = True
                continue
            (FileId, Repo, RepoOwner, RepoName, Branch, Path, FileExt, Size,
             Copies, PostId, PostTypeId, CommentId, SOUrl, GHUrl) = row
            if not CommentId:
                CommentId = None
            c.execute("""
                INSERT INTO PostReferenceGH
                    (FileId, Repo, RepoOwner, RepoName, Branch, Path, FileExt, Size,
                     Copies, PostId, PostTypeId, CommentId, SOUrl, GHUrl)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (FileId, Repo, RepoOwner, RepoName, Branch, Path, FileExt, Size,
             Copies, PostId, PostTypeId, CommentId, SOUrl, GHUrl))
            counter += 1
            if counter % commit_block == 0:
                conn.commit()  # must commit or all changes still in memory
                commit_counter += 1
                print("\tcommit no {}, elapsed: {}".format(
                    commit_counter, datetime.now() - t_start))
        print("\tPostReferenceGH took {} ({} rows)".format(
            datetime.now() - t_start, counter))
        c.execute("PRAGMA foreign_keys = ON;")
        conn.commit()
    print("7_load_postreferencegh done")


def load_ghmatches(conn):
    """8_load_ghmatches.sql"""
    c = conn.cursor()

    csv_filepath = os.path.join(script_dir, "GHMatches.csv")
    with open(csv_filepath) as csvfile:
        t_start = datetime.now()
        print("\tStarting GHMatches at {}".format(t_start))
        c.execute("PRAGMA foreign_keys = OFF;")
        csv_reader = reader(csvfile, delimiter=',', quotechar='"')
        counter = 0
        commit_counter = 0
        skipped_one = False
        for row in csv_reader:
            if not skipped_one:
                skipped_one = True
                continue
            (FileId, MatchedLine) = row
            MatchedLine = MatchedLine.replace('&#xD;&#xA;', '\n')
            c.execute("INSERT INTO GHMatches VALUES (?,?)", (FileId, MatchedLine))
            counter += 1
            if counter % commit_block == 0:
                conn.commit()  # must commit or all changes still in memory
                commit_counter += 1
                print("\tcommit no {}, elapsed: {}".format(
                    commit_counter, datetime.now() - t_start))
        print("\tGHMatches took {} ({} rows)".format(
            datetime.now() - t_start, counter))
        c.execute("PRAGMA foreign_keys = ON;")
        conn.commit()
    print("8_load_ghmatches done")


def create_sotorrent_indicies(conn):
    """9_create_sotorrent_indices.sql"""
    c = conn.cursor()
    c.execute("CREATE INDEX postblockdiff_index_1 ON PostBlockDiff(LocalId);")
    c.execute("CREATE INDEX postblockdiff_index_2 ON PostBlockDiff(PredLocalId);")

    c.execute("CREATE INDEX postblockversion_index_1 ON PostBlockVersion(LocalId);")
    c.execute("CREATE INDEX postblockversion_index_2 ON PostBlockVersion(PredLocalId);")
    c.execute("CREATE INDEX postblockversion_index_3 ON PostBlockVersion(RootLocalId);")
    c.execute("CREATE INDEX postblockversion_index_4 ON PostBlockVersion(PredSimilarity);")
    c.execute("CREATE INDEX postblockversion_index_5 ON PostBlockVersion(PredCount);")
    c.execute("CREATE INDEX postblockversion_index_6 ON PostBlockVersion(SuccCount);")
    c.execute("CREATE INDEX postblockversion_index_7 ON PostBlockVersion(Length);")
    c.execute("CREATE INDEX postblockversion_index_8 ON PostBlockVersion(LineCount);")

    c.execute("CREATE INDEX commenturl_index_1 ON CommentUrl(PostId);")

    c.execute("CREATE INDEX postreferencegh_index_1 ON PostReferenceGH(FileId);")
    c.execute("CREATE INDEX postreferencegh_index_2 ON PostReferenceGH(RepoName);")
    c.execute("CREATE INDEX postreferencegh_index_3 ON PostReferenceGH(Branch);")
    c.execute("CREATE INDEX postreferencegh_index_4 ON PostReferenceGH(FileExt);")
    c.execute("CREATE INDEX postreferencegh_index_5 ON PostReferenceGH(Size);")
    c.execute("CREATE INDEX postreferencegh_index_6 ON PostReferenceGH(Copies);")

    c.execute("CREATE INDEX titleversion_index_1 ON TitleVersion(PredEditDistance);")
    c.execute("CREATE INDEX titleversion_index_2 ON TitleVersion(SuccEditDistance);")

    c.execute("CREATE INDEX ghmatches_index_1 ON GHMatches(FileId);")
    print("9_create_sotorrent_indicies done")

def main():
    try:
        conn=connect(db_file)
        create_database(conn)           # 1_create_database
        load_so_from_xml(conn)          # 2_load_so_from_xml
        create_indicies(conn)           # 3_create_indices
        create_sotorrent_tables(conn)   # 4_create_sotorrent_tables
        # unnecessary                   # 5_create_sotorrent_user
        load_sotorrent(conn)            # 6_load_sotorrent
        load_postreferencegh(conn)      # 7_load_postreferencegh
        load_ghmatches(conn)            # 8_load_ghmatches
        create_sotorrent_indicies(conn) # 9_create_sotorrent_indicies

    except Error as e:
        print(e)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

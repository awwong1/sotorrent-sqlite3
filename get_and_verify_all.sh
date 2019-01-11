#!/usr/bin/env bash

function dl_and_verify_md5() {
  FILE="${1}";
  MD5HASH="${2}";

  if [ ! -f "${FILE}" ]; then
    wget https://zenodo.org/record/2273117/files/$FILE --output-document=$FILE
  fi;
  GENMD5HASH=`md5sum "${FILE}" | awk '{ print $1 }'`
  if [ "${GENMD5HASH}" == "${MD5HASH}" ]; then
    echo "${FILE} OK"
  else
    echo "${FILE} BAD"
  fi;
}

dl_and_verify_md5 1_create_database.sql e079bf0648e49e77aee5053a7170df4f
dl_and_verify_md5 2_load_so_from_xml.sql aeab3d449ec3f39a5c372475ef85bdf8
dl_and_verify_md5 3_create_indices.sql 4bf83b1ea7fbe7c5eeffb403c52bd402
dl_and_verify_md5 4_create_sotorrent_tables.sql dc71eaf388f5a7bf1815dada6ee90352
dl_and_verify_md5 5_create_sotorrent_user.sql e719b7d430dcbfc41e9149fd7be2cbbc
dl_and_verify_md5 6_load_sotorrent.sql cea4330cba80e2bec7a66dcc6270c0d3
dl_and_verify_md5 7_load_postreferencegh.sql a747635b8d2361ab07f16460f6436054
dl_and_verify_md5 8_load_ghmatches.sql 053033fbbc897272c6e98bd877d49d50
dl_and_verify_md5 9_create_sotorrent_indices.sql d3ee212014e05ba9fb924bce92c28c85
dl_and_verify_md5 Badges.xml.gz 781bd4cc1da8f0518011fa6ac0590c59
dl_and_verify_md5 Comments.xml.gz 2fb09435346d796cc7b08d8148ea771d
dl_and_verify_md5 CommentUrl.csv.gz 032869b4f42458855048e29edbf59d59
dl_and_verify_md5 GHMatches.csv.gz 5121b1659ede2e4f6ce77233cdcd973f
dl_and_verify_md5 LICENSE.md dd690a9239427df0ccf2369c97285125
dl_and_verify_md5 PostBlockDiff.csv.gz bd9a25996f530391b0dfd1f63273c1dd
dl_and_verify_md5 PostBlockVersion.csv.gz 78cba7e35e6169ea4b230174a195ace9
dl_and_verify_md5 PostHistory.xml.gz c3473175aa700784561043a4b420176f
dl_and_verify_md5 PostLinks.xml.gz 3673fd8815d409b8471734de3d01fbc0
dl_and_verify_md5 PostReferenceGH.csv.gz 61e0fe853e2b33c1063d54d96a805c3b
dl_and_verify_md5 Posts.xml.gz ff7cbf0c93cf8efabdd9512324d8a30b
dl_and_verify_md5 PostVersion.csv.gz fd8e444a05d25ffa7d473f17643c6f70
dl_and_verify_md5 PostVersionUrl.csv.gz 271e15da37247800bfa5e09441e5d830
dl_and_verify_md5 README.md 76e1d6694a2f7862dd5361fd1a9a1074
dl_and_verify_md5 Tags.xml.gz 45ade28bffb60ef9b05d0b5af62e599a
dl_and_verify_md5 TitleVersion.csv.gz 7f23f3308b1def66b32d4e5b5dff9995
dl_and_verify_md5 Users.xml.gz 0b0fb49c71a001582219db42394a5976
dl_and_verify_md5 Votes.xml.gz 42ae552fbdadb4bd4e02e26ec57fa070

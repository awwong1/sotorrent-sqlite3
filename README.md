# sotorrent-sqlite3

Load MSR 2019 Mining Challenge Data into `sqlite3`.
Tested on Debian 9 and Ubuntu 18.04 using Python3 with no external dependencies.

`get_and_verify_all.sh`:
- Download all `*.xml.gz` and `*.csv.gz` files from [https://zenodo.org/record/2273117](https://zenodo.org/record/2273117).

Run `gunzip *.gz` to unpack all archives.

Run `python3 main.py` to begin the creation of `sotorrent18_12.sqlite3`. This will take a long time (~2 Days).

## Terms of Use

**If you are in Abram's Winter 2019 CMPUT 663 class and are using this script or the sotorrent18_12.sqlite3 in your project, I would like to be listed as a co-author in your submission.**

To cite this work, please use the following:

```text
@misc{
  wong_2019,
  title={github.com:awwong1/sotorrent-sqlite3},
  url={https://github.com/awwong1/sotorrent-sqlite3},
  author={Alexander W. Wong},
  year={2019},
  month={Jan}
}
```

Please also refer to and cite the original work. [https://github.com/sotorrent/db-scripts/tree/master/sotorrent](https://github.com/sotorrent/db-scripts/tree/master/sotorrent)

```text
@inproceedings{DBLP:conf/msr/BaltesDT008,
  author    = {Sebastian Baltes and
               Lorik Dumani and
               Christoph Treude and
               Stephan Diehl},
  title     = {SOTorrent: reconstructing and analyzing the evolution of stack overflow
               posts},
  booktitle = {Proceedings of the 15th International Conference on Mining Software
               Repositories, {MSR} 2018, Gothenburg, Sweden, May 28-29, 2018},
  pages     = {319--330},
  year      = {2018},
  crossref  = {DBLP:conf/msr/2018},
  url       = {https://doi.org/10.1145/3196398.3196430},
  doi       = {10.1145/3196398.3196430},
  timestamp = {Mon, 07 Jan 2019 17:17:42 +0100},
  biburl    = {https://dblp.org/rec/bib/conf/msr/BaltesDT008},
  bibsource = {dblp computer science bibliography, https://dblp.org}
}

@proceedings{DBLP:conf/msr/2018,
  editor    = {Andy Zaidman and
               Yasutaka Kamei and
               Emily Hill},
  title     = {Proceedings of the 15th International Conference on Mining Software
               Repositories, {MSR} 2018, Gothenburg, Sweden, May 28-29, 2018},
  publisher = {{ACM}},
  year      = {2018},
  url       = {http://dl.acm.org/citation.cfm?id=3196398},
  timestamp = {Mon, 23 Jul 2018 13:46:25 +0200},
  biburl    = {https://dblp.org/rec/bib/conf/msr/2018},
  bibsource = {dblp computer science bibliography, https://dblp.org}
}
```



## License

[Apache V2](LICENSE).

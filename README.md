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
  title={awwong1/sotorrent-sqlite3},
  url={https://github.com/awwong1/sotorrent-sqlite3},
  journal={awwong1/sotorrent-sqlite3},
  publisher={GitHub},
  author={Wong, Alexander W},
  year={2019},
  month={Jan}
}
```

## License

[Apache V2](LICENSE).

# qb rankings

This project extracts NFL quarterback data from Pro Football Reference, Football Outsiders, and Over the Cap, transforms and combines the data, and loads to a SQLite database.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Installation

Fork and clone the repository

```bash
git clone https://github.com/[your username]/qb_rankings.git
```

Navigate to the repo directory

```bash
cd [clone path]/qb_rankings
```

Create conda environment to install required packages

```bash
conda env create --file=environment.yaml
```

Activate the newly created environment

```bash
conda activate qb_rankings_env
```

If you have issues with the environment after creation, you can remove it with the following

```bash
conda env remove -n qb_rankings_env
```

### Run Instructions

Update ```bgn_yr``` and ```end_yr``` in Makefile to set the range of years of data to extract and load to the database.

Make data and log folders if they don't already exist

```bash
make dirs
```

Clean out the data and log folders

```bash
make clean
```

Extract all seasons between ```bgn_yr``` and ```end_yr``` inclusive and export csv. Default is 2002 through 2019 (current era division formats)

```bash
make extract
```

The following will run all commands to recreate the database and reload data.

```bash
make all
```

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* <https://www.pro-football-reference.com/>
* <https://www.footballoutsiders.com/>
* <https://overthecap.com/>

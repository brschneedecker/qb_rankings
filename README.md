# qb rankings

This project extracts NFL quarterback data from Pro Football Reference, Football Outsiders, and Over the Cap, transforms and combines the data, and loads to a SQLite database.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Installation

Clone the repository

```bash
git clone https://github.com/brschneedecker/qb_rankings.git
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
conda-env remove -n qb_rankings_env
```

### Run Instructions

Update ```bgn_yr``` and ```end_yr``` in Makefile to set the range of years of data to extract and load to the database.

Run ```make db``` to Create the database with empty tables

```bash
make db
```

Extract all seasons between ```bgn_yr``` and ```end_yr``` inclusive and load to database. Default is 2002 through 2019 (current era division formats)

```bash
make extract
```

If you need to recreate the database, run the following to delete it.

```bash
make rm_db
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

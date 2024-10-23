
# Flight Delays Prediction Model

This project provides a predictive model for forecasting the number of flights for a given date, with optional filtering by origin, destination, airline, carrier group, flight type, and flight status (scheduled or charter).

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Data](#data)
- [Arguments](#arguments)
- [Example](#example)
- [Directory Structure](#directory-structure)
- [License](#license)

## Installation

### Step 1: Clone the repository

```bash
git clone <repo-url>
cd flight-delays
```

### Step 2: Set up Python environment

This project uses `pyenv` for managing Python environments. Ensure that you have `pyenv` installed. To set up the environment:

```bash
# Install the required Python version
pyenv install <python-version>

# Create and activate a virtual environment
pyenv virtualenv <python-version> modelenv
pyenv activate modelenv
```

### Step 3: Install dependencies

After activating the environment, install the required dependencies:

```bash
pip install -r requirements.txt
```

### Step 4: Download the data

The script requires flight departure data. You can download the data from the following link:

[US International Air Traffic Data](https://www.kaggle.com/datasets/parulpandey/us-international-air-traffic-data?resource=download)

Once downloaded, place the data in the `prediction-model/data` folder.

## Usage

You can run the `predictive-model.py` script from the command line. Use the `--date` option to specify the date you want predictions for, and other optional arguments to filter by specific criteria like origin, destination, airline, etc.

```bash
python prediction-model/predictive-model.py --date YYYY-MM-DD [options]
```

## Data

The data used for predictions comes from the US International Air Traffic Data available on Kaggle. Ensure the CSV file `International_Report_Departures.csv` is placed in the `prediction-model/data` directory.

## Arguments

The script accepts the following arguments:

- `--date` (required): The date for which you want to predict the number of flights (format: `YYYY-MM-DD`).
- `--origin` (optional): US airport code (e.g., JFK, LAX) to filter flights departing from a specific airport.
- `--destination` (optional): Airport code (e.g., LHR, CDG) to filter flights arriving at a specific airport.
- `--airline` (optional): Airline code (e.g., DL for Delta, AA for American Airlines).
- `--carriergroup` (optional): Carrier group code to filter by airline group.
- `--flight_type` (optional): Type of flight (e.g., Departures).
- `--scheduled` (optional): Filter by scheduled flights (`1` for scheduled, `0` for non-scheduled).
- `--charter` (optional): Filter by charter flights (`1` for charter, `0` for non-charter).

## Example

Predict flights for the date `2024-12-01` departing from JFK:

```bash
python prediction-model/predictive-model.py --date 2024-12-01 --origin JFK
```

Output:

```bash
Predicted Total Flights on closest date 2024-11-30: 150.42
Prediction Range: 140.12 to 160.70
```

## Directory Structure

```
├── .vscode/
│   └── launch.json
├── prediction-model/
│   ├── data/
│   ├── modelenv/
│   ├── output/
│   ├── scripts/
│   └── predictive-model.py
├── .gitignore
├── requirements.txt
└── README.md
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

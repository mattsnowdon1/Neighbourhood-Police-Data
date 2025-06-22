import requests as reqs
import pandas as pd
import numpy as np


def get_list_of_neighbourhoods() -> list[dict]:
    while True:
        force = input("Please enter a police force: ").lower()
        data = reqs.get(f"https://data.police.uk/api/{force}/neighbourhoods")
        if data.status_code == 200:
            return force, data.json()
        print("Invalid force, please try again")


def list_all_neighbourhoods(neighbourhoods: list[dict]) -> None:
    for neighbourhood in neighbourhoods:
        print(neighbourhood["name"])
    return input("Please enter a neighbourhood: ")


def get_neighbourhood(neighbourhoods: list[dict]) -> dict:
    while True:
        user_neighbourhood = input(
            "Please enter a neighbourhood in that force, or for a list of neighbourhoods press return: ").lower()

        if user_neighbourhood == "":
            user_neighbourhood = list_all_neighbourhoods(
                neighbourhoods).lower()

        for town_info in neighbourhoods:
            if town_info["name"].lower() == user_neighbourhood:
                return town_info
        print("Invalid neighbourhood, please try again")


def get_boundary(force: str, neighbourhood_id: str) -> str:
    data = reqs.get(
        f"https://data.police.uk/api/{force}/{neighbourhood_id}/boundary").json()
    output = ""

    for coord in data:
        output += f"{coord["latitude"]},{coord["longitude"]}:"

    return output[:-1]


def get_crimes(poly: str) -> pd.DataFrame:
    all_crimes = []
    for i in range(1, 13):
        all_crimes += reqs.post(
            "https://data.police.uk/api/crimes-street/all-crime", data={"date": f"2024-{str(i)}", "poly": poly}).json()
    return pd.DataFrame.from_dict(all_crimes)


def extract_location(location: dict):
    latitude = float(location["latitude"])
    longitude = float(location["longitude"])
    location_id = int(location["street"]["id"])
    location_name = location["street"]["name"]

    return latitude, longitude, location_id, location_name


def extract_outcome(outcome: dict):
    if outcome is None:
        return np.nan, np.nan

    outcome_status = outcome.get("category")
    outcome_date = outcome.get("date")

    return outcome_status, outcome_date


def clean_data():
    crimes[["latitude", "longitude", "location_id", "location_name"]] = crimes["location"].apply(
        lambda x: pd.Series(extract_location(x)))
    crimes.drop(columns=["location"], inplace=True)

    crimes[["outcome", "outcome_date"]] = crimes["outcome_status"].apply(
        lambda x: pd.Series(extract_outcome(x)))
    crimes.drop(columns=["outcome_status"], inplace=True)

    crimes["outcome_date"] = pd.to_datetime(
        crimes["outcome_date"], format="%Y-%m")
    crimes["month"] = pd.to_datetime(crimes["month"], format="%Y-%m")

    crimes["context"] = crimes["context"].replace("", np.nan)


if __name__ == "__main__":
    force, list_of_neighbourhoods = get_list_of_neighbourhoods()
    neighbourhood = get_neighbourhood(list_of_neighbourhoods)
    poly = get_boundary(force, neighbourhood["id"])
    crimes = get_crimes(poly)

    clean_data()

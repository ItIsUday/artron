import os

import pandas as pd

SECTORS = range(1, 27)
CACHE_FILE = "exofop_toi.csv"


def get_toi_df() -> pd.DataFrame:
    """
    Fetch ExoFOP TOIs list, caching the CSV locally.

    :return: TOIs list as a pandas.DataFrame
    """
    exofop_toi_url = "https://exofop.ipac.caltech.edu/tess/download_toi.php?sort=toi?&output=csv"

    if os.path.exists(CACHE_FILE):
        print(f"Loading TOI data from cache: {CACHE_FILE}")
        toi_df = pd.read_csv(CACHE_FILE)
    else:
        print(f"Downloading TOI data from: {exofop_toi_url}")
        toi_df = pd.read_csv(exofop_toi_url)
        toi_df.to_csv(CACHE_FILE, index=False)
        print(f"Cached TOI data to: {CACHE_FILE}")

    return toi_df


def filter_positive_toi_df(toi_df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter TOIs which are confirmed planets.

    :param toi_df: TOIs list as a pandas.DataFrame
    :return: TOIs list as a pandas.DataFrame
    """
    return toi_df[toi_df['TFOPWG Disposition'].isin(['CP', 'KP'])]


def get_tic_to_sectors(toi_df: pd.DataFrame) -> dict[int, list[int]]:
    """
    Given the toi_df, it generates a dictionary mapping TIC ID to list of sectors in the given range.

    :param toi_df: TOIs list as a pandas.DataFrame
    :return: The aforementioned dictionary
    """
    tic_dict = {}
    for tic, sectors in zip(toi_df['TIC ID'], toi_df['Sectors']):
        sectors = list(filter(lambda sector: sector in SECTORS, map(int, sectors.split(','))))
        if sectors:
            tic_dict[tic] = sectors

    return tic_dict


def main():
    toi_df = get_toi_df()
    toi_df = filter_positive_toi_df(toi_df)
    tic_to_sectors = get_tic_to_sectors(toi_df)


if __name__ == "__main__":
    main()

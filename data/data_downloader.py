import os
from typing import Mapping, Iterable

import pandas as pd
from astroquery.mast import MastMissions, MastMissionsClass

CONSIDERED_SECTORS = range(1, 27)
EXOFOP_TOI_URL = (
    "https://exofop.ipac.caltech.edu/tess/download_toi.php?sort=toi?&output=csv"
)
Sector = str
TOI_ID = str


def get_toi_df(url: str) -> pd.DataFrame:
    """
    Fetch ExoFOP TOIs list, caching the CSV locally.
    :param url: ExoFOP TESS table URL

    :return: TOIs list as a pandas.DataFrame
    """
    cache_file = "exofop_toi.csv"
    if os.path.exists(cache_file):
        print(f"Loading TOI data from cache: {cache_file}")
        toi_df = pd.read_csv(cache_file)
    else:
        print(f"Downloading TOI data from: {url}")
        toi_df = pd.read_csv(url)
        toi_df.to_csv(cache_file, index=False)
        print(f"Cached TOI data to: {cache_file}")

    return toi_df


def filter_positive_toi_df(toi_df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter TOIs which are confirmed planets.

    :param toi_df: TOIs list as a pandas.DataFrame
    :return: TOIs list as a pandas.DataFrame
    """
    return toi_df[toi_df["TFOPWG Disposition"].isin(["CP", "KP"])]


def get_tic_to_sectors(toi_df: pd.DataFrame) -> Mapping[TOI_ID, Iterable[Sector]]:
    """
    Given the toi_df, it generates a dictionary mapping TIC ID to list of sectors in the given range.

    :param toi_df: TOIs list as a pandas.DataFrame
    :return: The aforementioned dictionary
    """
    tic_dict = {}
    for tic, sectors in zip(toi_df["TIC ID"], toi_df["Sectors"]):
        sectors = list(
            filter(lambda sector: int(sector) in CONSIDERED_SECTORS, sectors.split(","))
        )
        if sectors:
            tic_dict[tic] = sectors

    return tic_dict


def generate_uri(tic: str, sector: str) -> str:
    """
    Given a TIC ID and a sector, generate the TESS SPOC URI.

    :param tic: TIC ID
    :param sector: The sector of the TIC
    :return: The URI
    """
    tic = tic.rjust(16, "0")
    sector = "s" + sector.rjust(4, "0")
    target = "/".join(tic[i : i + 4] for i in range(0, len(tic), 4))

    uri = f"mast:HLSP/tess-spoc/{sector}/target/{target}/hlsp_tess-spoc_tess_phot_{tic}-{sector}_tess_v1_lc.fits"
    return uri


def download_fits_of_tic(
    mission: MastMissionsClass, tic: str, sector: str, path: str
) -> None:
    """
    Download the lightcurve FITS files for a given TIC ID and a sector.

    :param mission: The TESS MastMission object
    :param tic: The TIC ID
    :param sector: The sector of the TIC
    :param path: The path to save the FITS files to
    :return:
    """
    result = mission.download_file(generate_uri(tic, sector), local_path=path)
    print(result)


def download_fits(tic_to_sectors: Mapping[str, Iterable[str]], path: str) -> None:
    """
    Download the lightcurve FITS files.

    :param tic_to_sectors: A dictionary mapping TIC ID to list of sectors.
    :param path: The path to save the FITS files to
    :return:
    """
    mission = MastMissions(mission="tess")

    for tic, sectors in tic_to_sectors.items():
        for sector in sectors:
            download_fits_of_tic(mission, tic, sector, path)


def main():
    toi_df = get_toi_df(EXOFOP_TOI_URL)
    toi_df = filter_positive_toi_df(toi_df)
    tic_to_sectors = get_tic_to_sectors(toi_df)
    download_fits(tic_to_sectors, "positive")


if __name__ == "__main__":
    main()

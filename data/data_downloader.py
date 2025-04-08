import os

import pandas as pd

SECTORS = range(1, 27)


def get_toi_df() -> pd.DataFrame:
    """
    Fetch ExoFOP TOIs list, caching the CSV locally.

    :return: TOIs list as a pandas.DataFrame
    """
    exofop_toi_url = "https://exofop.ipac.caltech.edu/tess/download_toi.php?sort=toi?&output=csv"
    cache_file = "exofop_toi.csv"
    if os.path.exists(cache_file):
        print(f"Loading TOI data from cache: {cache_file}")
        toi_df = pd.read_csv(cache_file)
    else:
        print(f"Downloading TOI data from: {exofop_toi_url}")
        toi_df = pd.read_csv(exofop_toi_url)
        toi_df.to_csv(cache_file, index=False)
        print(f"Cached TOI data to: {cache_file}")

    return toi_df


def filter_positive_toi_df(toi_df: pd.DataFrame) -> pd.DataFrame:
    """
    Filter TOIs which are confirmed planets.

    :param toi_df: TOIs list as a pandas.DataFrame
    :return: TOIs list as a pandas.DataFrame
    """
    return toi_df[toi_df['TFOPWG Disposition'].isin(['CP', 'KP'])]


def get_tic_to_sectors(toi_df: pd.DataFrame) -> dict[str, list[str]]:
    """
    Given the toi_df, it generates a dictionary mapping TIC ID to list of sectors in the given range.

    :param toi_df: TOIs list as a pandas.DataFrame
    :return: The aforementioned dictionary
    """
    tic_dict = {}
    for tic, sectors in zip(toi_df['TIC ID'], toi_df['Sectors']):
        sectors = list(filter(lambda sector: sector in SECTORS, sectors.split(',')))
        if sectors:
            tic_dict[tic] = sectors

    return tic_dict


def generate_uri(tic: str, sector: str) -> str:
    tic = tic.rjust(16, '0')
    sector = 's' + sector.rjust(4, '0')
    target = '/'.join(tic[i:i + 4] for i in range(0, len(tic), 4))

    uri = f"mast:HLSP/tess-spoc/{sector}/target/{target}/hlsp_tess-spoc_tess_phot_{tic}-{sector}_tess_v1_lc.fits"
    return uri


def download_fits_of_tic(mission, tic: str, sector: int) -> None:
    result = mission.download_file(generate_uri(tic, sector), local_path="")
    print(result)


def main():
    toi_df = get_toi_df()
    toi_df = filter_positive_toi_df(toi_df)
    tic_to_sectors = get_tic_to_sectors(toi_df)


if __name__ == "__main__":
    main()

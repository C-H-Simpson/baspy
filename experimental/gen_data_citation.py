"""
Charles Simpson 2020-10-13
Script for generating data citations for CMIP6 data, for compliance with CMIP6 terms.
"""
import baspy as bp
import pandas as pd
import requests
import xml.etree.ElementTree as ET


def generate_citation(
    MIP: str, Centre: str, Model: str, Experiment: str, Version: str,
) -> dict:
    """Generate a data citation from minimum necessary information.

    The input is used to query CERA.
    Metadata are downloaded as XML, and formatted as a citation string.
    Input names follow baspy column names, as strings.
    Output is a dictionary, including a citation string.

    Example input:
        MIP='CMIP',
        Centre='MOHC',
        Model='HadGEM3-GC31-LL',
        Experiment='historical',
        Version='v20190624
    Example output:
        {'MIP': 'CMIP', 'Centre': 'MOHC', 'Model': 'HadGEM3-GC31-LL', 'Experiment': 'historical', 'Version': 'v20190624', 'doi': '10.22033/ESGF/CMIP6.6109', 'publisher': 'Earth System Grid Federation', 'publicationYear': '2019', 'givenNames': ['Jeff', 'Matthew', 'Till', 'Martin', 'Tim'], 'familyNames': ['Ridley', 'Menary', 'Kuhlbrodt', 'Andrews', 'Andrews'], 'names': ['Ridley, J.', 'Menary, M.', 'Kuhlbrodt, T.', 'Andrews, M.', 'Andrews, T.'], 'citation': 'Ridley, J., Menary, M., Kuhlbrodt, T., Andrews, M., Andrews, T. (2019). MOHC HadGEM3-GC31-LL model output prepared for CMIP6 CMIP historical. v20190624. Earth System Grid Federation. https://doi.org/10.22033/ESGF/CMIP6.6109'}

    """
    url = (
        "https://cera-www.dkrz.de/WDCC/ui/cerasearch/cerarest/"
        + f"exportcmip6?input=CMIP6.{MIP}.{Centre}.{Model}.{Experiment}"
        + "&wt=XML"
    )
    response = requests.get(url)
    xml = response.text

    root = ET.fromstring(xml)

    root.tag
    root.attrib

    doi = ""
    publisher = ""
    publicationYear = ""
    givenNames = []
    familyNames = []

    for child in root:
        if "identifier" in child.tag and child.attrib["identifierType"] == "DOI":
            doi = child.text
        elif "creators" in child.tag:
            for creator in list(child):
                for x in list(creator):
                    if "givenName" in x.tag:
                        givenNames.append(x.text)
                    elif "familyName" in x.tag:
                        familyNames.append(x.text)
        elif "publisher" in child.tag:
            publisher = child.text
        elif "publicationYear" in child.tag:
            publicationYear = child.text

    initials = [".".join([c for c in s if c.isupper()]) + "." for s in givenNames]
    names = [", ".join([a, b]) for a, b in zip(familyNames, initials)]

    citation = (
        ", ".join(names)
        + f" ({publicationYear}). {Centre} {Model} model output prepared for CMIP6 {MIP} {Experiment}. {Version}. {publisher}. https://doi.org/{doi}"
    )

    return {
        "MIP": MIP,
        "Centre": Centre,
        "Model": Model,
        "Experiment": Experiment,
        "Version": Version,
        "doi": doi,
        "publisher": publisher,
        "publicationYear": publicationYear,
        "givenNames": givenNames,
        "familyNames": familyNames,
        "names": names,
        "citation": citation,
    }


def df_to_citations(df: pd.DataFrame) -> pd.DataFrame:
    """Generate data citations from a baspy dataframe.

    Input: dataframe of model runs generated by baspy
    Output: dataframe with citations generated.
    """
    results = []
    for row in df.itertuples():
        results.append(
            generate_citation(
                row.MIP, row.Centre, row.Model, row.Experiment, row.Version
            )
        )
    return pd.DataFrame(results)


if __name__ == "__main__":
    experiments = ()

    # Get some data with baspy
    catlg = bp.catalogue(
        dataset="cmip6",
        Experiment=["historical", "ssp245",],
        CMOR="day",
        Var=["tas", "hurs", "tasmax", "tasmin"],
        complete_var_set=True,
    )
    print("Demo generate_citation")
    print(
        generate_citation(
            MIP="CMIP",
            Centre="MOHC",
            Model="HadGEM3-GC31-LL",
            Experiment="historical",
            Version="v20190624",
        )
    )

    print("Demo generate_citations")
    print(df_to_citations(catlg.sample(5).reset_index(drop=True))["citation"])
"""Required for pip install -e ."""


from setuptools import setup

setup(
    entry_points={
        "console_scripts": [
            "dc-uvotimage=uvotimage:main",
            "dc-uvotskycorr=uvotskycorr:main",
            "dc-uvotattcorr=uvotattcorr:main",
            "dc-uvotimage2=uvotimage2:main",
            "dc-uvotbadpix=uvotbadpix:main",
            "dc-uvotexpmap=uvotexpmap:main",
            "dc-uvotskycorr2=uvotskycorr2:main",
            "dc-uvotskylss=uvotskylss:main",
            "dc-sort_by_year=sort_by_year:main",
            "dc-uvotimsum=uvotimsum:main",
            "dc-corrections=corrections:main",
            "dc-combine=combine:main",
            "dc-calibration=calibration:main",
            "dc-header_info=header_info:main",
            "dc-collect_images=collect_images:main",
        ],
    },
)

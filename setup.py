"""Required for pip install -e ."""


from setuptools import setup

setup(
    entry_points={
        "console_scripts": [
            "uvotimage=uvotimage:main",
            "uvotskycorr=uvotskycorr:main",
            "uvotattcorr=uvotattcorr:main",
            "uvotimage2=uvotimage2:main",
            "uvotbadpix=uvotbadpix:main",
            "uvotexpmap=uvotexpmap:main",
            "uvotskycorr2=uvotskycorr2:main",
            "uvotskylss=uvotskylss:main",
            "sort_by_year=sort_by_year:main",
            "uvotimsum=uvotimsum:main",
            "corrections=corrections:main",
            "combine=combine:main",
            "calibration=calibration:main",
            "header_info=header_info:main",
            "collect_images=collect_images:main",
        ],
    },
)

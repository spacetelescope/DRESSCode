"""Required for pip install -e ."""


from setuptools import setup

setup(
    entry_points={
        "console_scripts": [
            "uvotimage=dresscode.uvotimage:main",
            "uvotskycorr=dresscode.uvotskycorr:main",
            "uvotattcorr=dresscode.uvotattcorr:main",
            "uvotimage2=dresscode.uvotimage2:main",
            "uvotbadpix=dresscode.uvotbadpix:main",
            "uvotexpmap=dresscode.uvotexpmap:main",
            "uvotskycorr2=dresscode.uvotskycorr2:main",
            "uvotskylss=dresscode.uvotskylss:main",
            "sort_by_year=dresscode.sort_by_year:main",
            "uvotimsum=dresscode.uvotimsum:main",
            "corrections=dresscode.corrections:main",
            "combine=dresscode.combine:main",
            "calibration=dresscode.calibration:main",
        ],
    },
)

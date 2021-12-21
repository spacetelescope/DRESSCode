"""Required for pip install -e ."""


from setuptools import setup

setup(
    entry_points={
        "console_scripts": [
            "dc-uvotimage=dresscode.uvotimage:main",
            "dc-uvotskycorr=dresscode.uvotskycorr:main",
            "dc-uvotattcorr=dresscode.uvotattcorr:main",
            "dc-uvotimage2=dresscode.uvotimage2:main",
            "dc-uvotbadpix=dresscode.uvotbadpix:main",
            "dc-uvotexpmap=dresscode.uvotexpmap:main",
            "dc-uvotskycorr2=dresscode.uvotskycorr2:main",
            "dc-uvotskylss=dresscode.uvotskylss:main",
            "dc-uvotimsum=dresscode.uvotimsum:main",
            "dc-corrections=dresscode.corrections:main",
            "dc-combine=dresscode.combine:main",
            "dc-calibration=dresscode.calibration:main",
            "dc-header_info=dresscode.header_info:main",
            "dc-collect_images=dresscode.collect_images:main",
        ],
    },
)

"""
This script loads every ABF in the data folder and generates a summary of its
header (in both HTML and markdown format).
"""

import matplotlib.pyplot as plt
import pytest
import glob
import os
import sys
PATH_HERE = os.path.abspath(os.path.dirname(__file__))
PATH_PROJECT = os.path.abspath(PATH_HERE+"/../")
PATH_DATA = os.path.abspath(PATH_PROJECT+"/data/abfs/")
PATH_HEADERS = os.path.abspath(PATH_PROJECT+"/data/headers/")

try:
    # this ensures pyABF is imported from this specific path
    sys.path.insert(0, "src")
    import pyabf
    from pyabf.abfHeaderDisplay import abfInfoPage
except:
    raise ImportError("couldn't import local pyABF")


@pytest.mark.first
def test_cookbook_deleteOldHeaderImages():
    for fname in glob.glob(PATH_HEADERS+'/*.png'):
        os.remove(fname)


@pytest.mark.last
def test_cookbook_createImageIndexPage():

    md = "# Sample ABFs\n\n"
    md += "This is a small collection of various ABFs I practice developing with. "
    md += "Many of them were emailed to me by contributors. If you have a unique type "
    md += "of ABF file, email it to me and I will include it here. Note that this page "
    md += "is generated automatically by [dataThumbnails.py](/tests/tests/dataThumbnails.py).\n\n"

    for fname in sorted(glob.glob(PATH_DATA+"/*.abf")):

        abf = pyabf.ABF(fname)
        abfIDsafe = abf.abfID.replace(" ", "%20")
        md += f"## {abf.abfID}.abf\n{abf}"
        md += f"<br>\n[View the full header](headers/{abfIDsafe}.md)"
        md += f"<a href='headers/{abfIDsafe}.png'><img src='headers/{abfIDsafe}.png'></a>"
        md += "\n\n"

    with open(PATH_PROJECT+"/data/readme.md", 'w') as f:
        f.write(md)


@pytest.mark.parametrize("abfPath", glob.glob("data/abfs/*.abf"))
def test_cookbook_createHeaderImages(abfPath):
    abf = pyabf.ABF(abfPath)
    assert isinstance(abf, pyabf.ABF)

    # create figure and subplots
    fig = plt.figure(figsize=(8, 6))
    fig.patch.set_alpha(0)  # transparent background
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
    ax1.grid(alpha=.4, ls='--')
    ax2.grid(alpha=.4, ls='--')
    ax1.patch.set_facecolor('w')
    ax2.patch.set_facecolor('w')
    ax1.set_xmargin(0)
    ax2.set_xmargin(0)

    # overlap or continuous view depends on protocol
    absoluteTime = False
    if "0111" in abf.protocol:
        absoluteTime = True
    if "loose" in abf.protocol:
        absoluteTime = True

    # usually we plot channel 0, but sometimes manually override
    channel = 0
    if "18702001" in abf.abfID:
        channel = 1

    # plot the data sweep by sweep
    maxSweepsToPlot = min(abf.sweepCount, 20)
    for sweep in range(maxSweepsToPlot):
        abf.setSweep(sweep, channel=channel, absoluteTime=absoluteTime)
        ax1.plot(abf.sweepX, abf.sweepY, alpha=.5, color='b', lw=.5)
        ax2.plot(abf.sweepX, abf.sweepC, color='r')

    # decorate plot and save it
    ax1.set_title(f"{abf.abfID}.abf [channel: {abf.sweepChannel+1}/{abf.channelCount}] [sweeps: {abf.sweepNumber+1}]")
    ax1.set_ylabel(abf.sweepLabelY)
    ax1.set_xlabel(abf.sweepLabelX)
    ax2.set_ylabel(abf.sweepLabelC)
    ax2.set_xlabel(abf.sweepLabelX)
    fig.tight_layout()
    ax1.margins(0, .1)
    ax2.margins(0, .1)
    fig.savefig(f"{PATH_HEADERS}/{abf.abfID}.png")
    plt.close()

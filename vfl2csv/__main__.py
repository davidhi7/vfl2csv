import sys
from pathlib import Path

from TrialSiteSheet import TrialSiteSheet

if __name__ == '__main__':
    trialSiteSheet = TrialSiteSheet(Path('res/daten.xlsx'), '09201_518a2')
    trialSiteSheet.write_data(Path('res/out.csv'))
    trialSiteSheet.write_metadata(Path('res/metadata.txt'))

    print('done')

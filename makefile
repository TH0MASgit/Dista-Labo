SHELL=/bin/bash

# Update scripts
update-all: update-dista update-logisticam

update-dista:
	git pull

update-logisticam:
	git subtree pull --prefix=logisticam/ --squash logisticam main

update-libs:
	scripts/setup_pip.sh

.PHONY: update-all update-dista update-logisticam update-libs


# Run scripts
nano-streamer:
	python3 streamer.py --csi --linuxid=0,1 --resolution=NANO --vflip=1

run-detection:
	python3 detection.py --opencv --resolution=VGA --view_2dbox -c localhost/1000

.PHONY: nano-streamer run-detection


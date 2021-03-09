rhqinstall() {
  cd /homes/pmcd/rh-queue
  rm -rf ./build
  python3 setup.py bdist_wheel -d /opt/rh-queue
  sudo -H -u root python3 -m pip install --upgrade /opt/rh-queue/*.whl --no-cache
  rm /opt/rh-queue/*.whl
}
rhqtest() {
  cd ~/rh-queue/testfiles
  deactivate
  for var in "$@"; do
    python3 "run_${var}_tests.py"
  done
  rhqstart
}
rhqstart() {
  source ~/venv/rhqueue/bin/activate
  cd ~/rh-queue
  python setup.py develop
}
rhqstop() {
  deactivate
}
slurm-update-conf() {
  cd ~/rh-queue/slurm-install-files/
  sudo cp slurm.conf /etc/slurm-llnl
  sudo cp gres.conf /etc/slurm-llnl
  cd $OLDPWD
}
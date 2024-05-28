source /cvmfs/mu2e.opensciencegrid.org/setupmu2e-art.sh
muse setup Offline
if [[ "$MU2E_SPACK" == "true" ]]; then
    source /exp/mu2e/app/users/edmonds/pytrkdb_temp/bin/activate
else
    setup pyana
fi

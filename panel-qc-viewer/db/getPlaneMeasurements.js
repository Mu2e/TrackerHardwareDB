const express = require('express');
const router = express.Router();
const fetch = require('node-fetch');

router
  .get('/:type/:plane_id', async(req, res, next) =>{
    const response = await fetch('https://dbdata0vm.fnal.gov:9443/QE/mu2e/prod/app/SQ/query?dbname=mu2e_tracker_prd&t=measurements.plane_'+req.params.type+'&w=plane_id:eq:'+req.params.plane_id+"&o=-date_taken&f=text");

    const repairsInfo = await response.text();
    return res.send(repairsInfo)
})

module.exports = router;

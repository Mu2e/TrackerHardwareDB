const express = require('express');
const router = express.Router();
const fetch = require('node-fetch');

router
  .get('/:type/:measure/:id', async(req, res, next) =>{
    const response = await fetch('https://dbdata0vm.fnal.gov:9443/QE/mu2e/prod/app/SQ/query?dbname=mu2e_tracker_prd&t=measurements.'+req.params.type+'_'+req.params.measure+'&w='+req.params.type+'_id:eq:'+req.params.id+"&o=-date_taken&f=text");

    const repairsInfo = await response.text();
    return res.send(repairsInfo)
})

module.exports = router;

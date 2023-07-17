const express = require('express');
const router = express.Router();
const fetch = require('node-fetch');

router
  .get('/:panel_id', async(req, res, next) =>{
    const response = await fetch('https://dbdata0vm.fnal.gov:9443/QE/mu2e/prod/app/SQ/query?dbname=mu2e_tracker_prd&t=repairs.panels&w=panel_id:eq:'+req.params.panel_id+"&o=-date_uploaded,-repair_id&f=text");

    const repairsInfo = await response.text();
    return res.send(repairsInfo)
})

module.exports = router;

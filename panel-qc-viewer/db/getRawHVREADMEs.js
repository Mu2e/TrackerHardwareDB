const express = require('express');
const router = express.Router();
const fetch = require('node-fetch');

router
  .get('/', async(req, res, next) =>{
    const response = await fetch('https://dbdata0vm.fnal.gov:9443/QE/mu2e/prod/app/SQ/query?dbname=mu2e_tracker_prd&t=qc.panel_hv_data_readmes&f=text');
    const hvDataInfo = await response.text();
    return res.send(hvDataInfo)
})

module.exports = router;

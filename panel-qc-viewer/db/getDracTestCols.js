const express = require('express');
const router = express.Router();
const fetch = require('node-fetch');

router
  .get('/', async(req, res, next) =>{
    const response = await fetch('https://dbdata0vm.fnal.gov:9443/QE/mu2e/prod/app/SQ/I/columns?dbname=mu2e_tracker_prd&t=drac.test_results&f=json');
    const panelInfo = await response.text();
    return res.send(panelInfo);
})

module.exports = router;

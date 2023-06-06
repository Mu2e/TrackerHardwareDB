const express = require('express');
const router = express.Router();
const fetch = require('node-fetch');

router
    .get('/', async(req, res, next) =>{
    const response = await fetch('https://dbdata0vm.fnal.gov:9443/QE/mu2e/prod/app/SQ/query?dbname=mu2e_tracker_prd&t=qc.panels&o=panel_id&f=text');
    const allPanelInfo = await response.text();
//	console.log(allPanelInfo);
    return res.send(allPanelInfo);
})

module.exports = router;

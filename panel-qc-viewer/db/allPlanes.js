const express = require('express');
const router = express.Router();
const fetch = require('node-fetch');

router
    .get('/', async(req, res, next) =>{
    const response = await fetch('https://dbdata0vm.fnal.gov:9443/QE/mu2e/prod/app/SQ/query?dbname=mu2e_tracker_prd&t=qc.planes&o=plane_id&w=plane_id:gt:0&f=text');
    const allPlaneInfo = await response.text();
//	console.log(allPlaneInfo);
    return res.send(allPlaneInfo);
})

module.exports = router;

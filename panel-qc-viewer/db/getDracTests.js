const express = require('express');
const router = express.Router();
const fetch = require('node-fetch');

router
  .get('/', async(req, res, next) =>{
    const response = await fetch('https://dbdata0vm.fnal.gov:9443/QE/mu2e/prod/app/SQ/query?dbname=mu2e_tracker_prd&t=drac.test_results&f=text');
    const panelInfo = await response.text();
    return res.send(panelInfo);
})

router
  .get('/:id', async(req, res, next) =>{
    const response = await fetch('https://dbdata0vm.fnal.gov:9443/QE/mu2e/prod/app/SQ/query?dbname=mu2e_tracker_prd&t=drac.test_results&w=drac_id:eq:'+req.params.id+'&f=text');
    const panelInfo = await response.text();
    return res.send(panelInfo);
})

module.exports = router;

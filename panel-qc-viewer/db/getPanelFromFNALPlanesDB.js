const express = require('express');
const router = express.Router();
const fetch = require('node-fetch');

router
  .get('/:id', async(req, res, next) =>{
    const response = await fetch('https://dbdata0vm.fnal.gov:9443/QE/mu2e/prod/app/SQ/query?dbname=mu2e_tracker_prd&t=imported.fnal_planes&w=panel_id:eq:'+req.params.id+'&f=text');
    const panelInfo = await response.text();
    return res.send(panelInfo);
})

router
  .get('/:id/:file', async(req, res, next) =>{
    const response = await fetch('https://dbdata0vm.fnal.gov:9443/QE/mu2e/prod/app/SQ/query?dbname=mu2e_tracker_prd&t=imported.fnal_planes&w=panel_id:eq:'+req.params.id+'&w=file_name:eq:' + req.params.file + '&f=text');
    const panelInfo = await response.text();
    return res.send(panelInfo);
})

module.exports = router;

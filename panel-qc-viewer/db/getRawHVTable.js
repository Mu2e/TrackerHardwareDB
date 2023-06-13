const express = require('express');
const router = express.Router();
const fetch = require('node-fetch');
const papa = require('papaparse') // for parsing csv

router
  .get('/:id/:ch', async(req, res, next) =>{
    const response = await fetch('https://dbdata0vm.fnal.gov:9443/QE/mu2e/prod/app/SQ/query?dbname=mu2e_tracker_prd&t=hvdata.panel'+req.params.id+'&c=timestamp,current'+req.params.ch+'&w=current'+req.params.ch+':ne:0');
    const hvData = await response.text();
//      console.log(hvData);
      var parse_config = {header: true, 
			  transformHeader:function(h) { // because the columns names are current00, current01 etc, it will be easier to loop through and plot if they were each called "current"
			      if (h.startsWith("current")) { return "current"; } 
			      else { return h; }
			  }
			 };
    return res.send(papa.parse(hvData, parse_config).data);
})

module.exports = router;

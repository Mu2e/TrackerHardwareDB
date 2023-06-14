const express = require('express');
const router = express.Router();

router
  .get('/', async(req, res, next) =>{
      res.render('hv_readmes', { title: 'Panel QC database viewer' });
});

module.exports = router;

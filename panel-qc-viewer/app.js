var createError = require('http-errors');
var express = require('express');
var path = require('path');
var cookieParser = require('cookie-parser');
var logger = require('morgan');
var cors = require('cors');

var indexRouter = require('./routes/index');
var usersRouter = require('./routes/users');

var app = express();

// view engine setup
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'pug');

app.use(cors());
app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(cookieParser());
app.use(express.static(path.join(__dirname, 'public')));

app.use('/', indexRouter);
app.use('/allPanels', require('./db/allPanels'));
app.use('/getPanel', require('./db/getPanel'));

app.use('/findPanels', require('./db/findPanels'));
app.use('/find_panel', require('./routes/find_panel'));

app.use('/hv_data', require('./routes/hv_data'));
app.use('/getRawHVData', require('./db/getRawHVData'));

app.use('/panel_qc', require('./routes/panel_qc'));
app.use('/all_panel_qc', require('./routes/all_panel_qc'));

app.use('/allPlanes', require('./db/allPlanes'));
app.use('/getPlane', require('./db/getPlane'));
app.use('/plane_qc', require('./routes/plane_qc'));

app.use('/getPanelFromFNALPlanesDB', require('./db/getPanelFromFNALPlanesDB'));
app.use('/getImportDateOfFNALPlanesDB', require('./db/getImportDateOfFNALPlanesDB'));
app.use('/fnal_plane_db', require('./routes/fnal_plane_db'));

app.use('/earboard', require('./routes/earboard'));

// catch 404 and forward to error handler
app.use(function(req, res, next) {
  next(createError(404));
});

// error handler
app.use(function(err, req, res, next) {
  // set locals, only providing error in development
  res.locals.message = err.message;
  res.locals.error = req.app.get('env') === 'development' ? err : {};

  // render the error page
  res.status(err.status || 500);
  res.render('error');
});

module.exports = app;

'use strict';

var gulp = require('gulp');
var gutil = require('gulp-util');

var babelify = require('babelify');
var browserify = require('browserify');
var buffer = require('vinyl-buffer');
var eslint = require('gulp-eslint');
var image = require('gulp-image');
var less = require('gulp-less');
var cleanCss = require('gulp-clean-css');
var rename = require('gulp-rename');
var source = require('vinyl-source-stream');
var sourcemaps = require('gulp-sourcemaps');
var uglify = require('gulp-uglify');
var watchify = require('watchify');

var fs = require('fs');
var glob = require('glob');
var del = require('del');

var limitless = '../limitless/static/limitless/';

// Source tasks

function getSources() {
  var sources = ['src/index.js'];

  function include(pattern) {
    var paths = glob.sync(pattern);
    paths.forEach(function(path) {
      sources.push(path);
    });
  };

  include('src/initializers/*.js');
  include('src/initializers/**/*.js');

  return sources.map(function(path) {
    return path;
  });
};

function lintjsapp() {
  return gulp.src('src/**/*.js')
    .pipe(eslint({
        'parser': 'babel-eslint',
        'parserOptions': {
            'ecmaVersion': 7,
            'sourceType': 'module',
            'ecmaFeatures': {
                'jsx': true
            }
        },
        rules: {
          "semi": ["error", "never"],
          "no-undef": "error",
          "strict": 2
        },
        globals: [
          "gettext",
          "ngettext",
          "interpolate",
          "limitless",
          "hljs"
        ],
        envs: [
            "browser",
            "jquery",
            "node",
            "es6"
        ]
    }))
    .pipe(eslint.format());
};

function fastsource() {
  process.env.NODE_ENV = 'development';

  return browserify({
      entries: getSources(),
      debug: true,
    })
    .external('moment')
    .external('cropit')
    .external('react')
    .external('react-dom')
    .external('react-router')
    .external('redux')
    .external('react-redux')
    .transform(babelify)
    .bundle()
    .pipe(source('limitless.js'))
    .pipe(buffer())
    .pipe(gulp.dest(limitless + 'js'));
};

function watchifybuild() {
  process.env.NODE_ENV = 'development';

  var b = browserify({
      entries: getSources(),
      debug: true,
      cache: {},
      packageCache: {}
    })
    .plugin(watchify, {
      delay: 100,
      poll: true
    })
    .external('moment')
    .external('cropit')
    .external('react')
    .external('react-dom')
    .external('react-router')
    .external('redux')
    .external('react-redux')
    .transform(babelify)
    .on('error', function(err) {
      gutil.log(gutil.colors.red(err.toString() + '\n' + err.codeFrame));
      this.emit('end');
    });

    function bundle() {
      b.bundle()
        .on('error', function(err) {
          gutil.log(gutil.colors.red(err.toString() + '\n' + err.codeFrame));
          this.emit('end');
        })
        .pipe(fs.createWriteStream(limitless + 'js/limitless.js'));
    }

    b.on('update', bundle);
    bundle();

    b.on('log', function (msg) {
      gutil.log(gutil.colors.cyan('watchify:'), msg);
    });
}

function jsapp() {
  process.env.NODE_ENV = 'production';

  return browserify({
      entries: getSources(),
      debug: false
    })
    .external('moment')
    .external('cropit')
    .external('react')
    .external('react-dom')
    .external('react-router')
    .external('redux')
    .external('react-redux')
    .transform(babelify, { sourceMaps: true })
    .bundle()
    .pipe(source('limitless.js'))
    .pipe(buffer())
    .pipe(sourcemaps.init({ loadMaps: true }))
    .pipe(uglify())
    .pipe(sourcemaps.write('./'))
    .pipe(gulp.dest(limitless + 'js'));
};

// Styles tasks

function cleanstyle() {
  return del(limitless + 'css', {force: true});
};

function faststyle() {
  return gulp.src('style/index.less')
    .pipe(less().on('error', function(err) {
        gutil.log(gutil.colors.red(err.toString()));
        this.emit('end');
      }))
    .pipe(rename('limitless.css'))
    .pipe(gulp.dest(limitless + 'css'));
};

function style() {
  return gulp.src('style/index.less')
    .pipe(less())
    .pipe(cleanCss({compatibility: 'ie11'}))
    .pipe(rename('limitless.css'))
    .pipe(gulp.dest(limitless + 'css'));
};

// Static tasks

function copyfonts() {
  return gulp.src('static/fonts/**/*')
    .pipe(gulp.dest(limitless + 'fonts'));
};

function copyimages() {
  return gulp.src('static/img/**/*')
    .pipe(image())
    .pipe(gulp.dest(limitless + 'img'));
};

const statics = gulp.parallel(copyfonts, copyimages);

// Vendor tasks
function vendors() {
  process.env.NODE_ENV = 'production';

  return browserify({
      entries: 'src/vendor.js',
      debug: false
    })
    .transform('browserify-shim')
    .require('moment')
    .require('cropit')
    .require('react')
    .require('react-dom')
    .require('react-router')
    .require('redux')
    .require('react-redux')
    .transform(babelify, { sourceMaps: true })
    .bundle()
    .pipe(source('vendor.js'))
    .pipe(buffer())
    .pipe(sourcemaps.init({ loadMaps: true }))
    .pipe(uglify())
    .pipe(sourcemaps.write('./'))
    .pipe(gulp.dest(limitless + 'js'));
};

function copyzxcvbn() {
  return gulp.src('node_modules/zxcvbn/dist/*')
    .pipe(gulp.dest(limitless + 'js'));
};

// Watchers

function watchjs() {
  gulp.watch('src/**/*.js', gulp.series(lintjsapp, watchifybuild));
}

function watchstyle() {
  gulp.watch('style/**/*.less', faststyle);
}

// Entry points

const buildstyle = gulp.series(cleanstyle, style);
const buildjsapp = gulp.series(lintjsapp, jsapp);

const build = gulp.parallel(
  buildstyle,
  statics,
  buildjsapp,
  vendors,
  copyzxcvbn
)

const watch = gulp.series(
  watchjs,
  watchstyle,
)

module.exports = {
  build,
  watch,
  watchstyle,
  lint: lintjsapp,
}
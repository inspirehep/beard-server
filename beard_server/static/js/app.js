/*
 * This file is part of INSPIRE.
 * Copyright (C) 2016 CERN.
 *
 * INSPIRE is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of the
 * License, or (at your option) any later version.
 *
 * INSPIRE is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with INSPIRE; if not, write to the Free Software Foundation, Inc.,
 * 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
* In applying this license, CERN does not
* waive the privileges and immunities granted to it by virtue of its status
* as an Intergovernmental Organization or submit itself to any jurisdiction.
*/

var app = angular.module('beard', ['ngSanitize']);

app.controller('BeardController', ['$scope', '$http', function($scope, $http) {
  $scope.getSampleClusters = function() {
    var signatures = [
      {
        "author_affiliation": "Taiwan, Natl. Chiao Tung U.",
        "author_name": "Wang, Shang-Yung",
        "publication_id": 1395222,
        "signature_id": "Wang_1395222"
      }, {
        "author_affiliation": "Taiwan, Natl. Chiao Tung U.",
        "author_name": "Wang, Shang-Yung",
        "publication_id": 428605,
        "signature_id": "Wang_428605"
      }, {
        "author_affiliation": "Taiwan, Natl. Chiao Tung U.",
        "author_name": "Lin, Shih-Yuin",
        "publication_id": 428605,
        "signature_id": "Lin_428605"
      }
    ];

    $scope.clustersSignatures = JSON.stringify(signatures, null, '  ');

    var clusters = [
      {
        "title": "Towards graphene-based detectors for dark matter " +
          "directional detection",
        "year": 2015,
        "publication_id": 1395222,
        "authors": ["Wang, Shang-Yung"]
      }, {
        "title": "Induced Einstein-Kalb-Ramond theory and the black hole",
        "year": 1996,
        "publication_id": 428605,
        "authors": [
          "Kao, W.F.",
          "Chyi, Tzuu-Kang",
          "Dai, W.B.",
          "Wang, Shang-Yung",
          "Lin, Shih-Yuun"
        ]
      }
    ];

    $scope.clustersRecords = JSON.stringify(clusters, null, '  ');
  }

  $scope.getSamplePhoneticBlock = function() {
    $scope.fullName = "John Smith";
  }

  $scope.getSamplePublication = function() {
    $scope.publicationTitle = "Discovery of a Long-Lived,"
      + "High Amplitude Dusty Infrared Transient";

    $scope.publicationAbstract = "We report the detection "
      + "of an infrared selected transient which has lasted "
      + "at least 5 years, first identified by a large mid-infrared and "
      + "optical outburst from a faint X-ray source detected with the Chandra "
      + "X-ray Observatory. In this paper we rule out several scenarios for "
      + "the cause of this outburst, including a classical nova, a luminous "
      + "red nova, AGN flaring, a stellar merger, and intermediate luminosity "
      + "optical transients, and interpret this transient as the result of a "
      + "Young Stellar Object (YSO) of at least solar mass accreting material "
      + "from the remains of the dusty envelope from which it formed, in "
      + "isolation from either a dense complex of cold gas or massive star "
      + "formation. This object does not fit neatly into other existing "
      + "categories of large outbursts of YSOs (FU Orionis types) which may be "
      + "a result of the object's mass, age, and environment. It is also "
      + "possible that this object is a new type of transient unrelated "
      + "to YSOs.";

    $scope.publicationCategory = ["astro-ph"];
  }

  $scope.submitClusters = function() {
    if ($scope.clustersRecords == null ||
        $scope.clustersSignatures == null) {
      return;
    }

    NProgress.configure({ parent: '#clustering-modal' });
    NProgress.start();

    getClusters(
      $scope.clustersRecords,
      $scope.clustersSignatures
    );
  }

  $scope.submitPhoneticBlock = function() {
    if ($scope.fullName == null) {
      return;
    }

    NProgress.configure({ parent: '#text-modal' });
    NProgress.start();

    getPhoneticBlock($scope.fullName);
  }

  $scope.submitPredictor = function() {
    if ($scope.publicationAbstract == null ||
        $scope.publicationCategory == null ||
        $scope.publicationTitle == null) {
      return;
    }

    NProgress.configure({ parent: '#predictor-modal' });
    NProgress.start();

    getPrediction(
      $scope.publicationAbstract,
      $scope.publicationCategory,
      $scope.publicationTitle
    );
  }

  var getClusters = function(records, signatures) {
    if (records == null || signatures == null) {
      return;
    }

    var clusteringData = {
      signatures: JSON.parse(signatures),
      records: JSON.parse(records)
    };

    $http.post("/api/clustering/clusters", clusteringData)
    .success(function(data) {
      // Workaround.
      $scope.clusteringHTML = '<table class="table"><thead><tr>' +
                              '<th>Person #</th><th>Signatures</th></thead>' +
                              '<tbody>';

      for (var index in data) {
        if (data.hasOwnProperty(index)) {
          var cluster = data[index].join(', ');
          var row = '<tr><th scope="row">' + index + '</th>' +
                    '<td>' + cluster + '</td></tr>';

          $scope.clusteringHTML += row;
        }
      }

      $scope.clusteringHTML += '</tbody></table>';
      NProgress.done();
    });
  }

  var getPhoneticBlock = function(name) {
    if (name == null) {
      return;
    }

    var fullNames = {
      full_names: [name]
    };

    $http.post("/api/text/phonetic_blocks", fullNames)
    .success(function(data) {
      $scope.phonetic = data.phonetic_blocks[name];

      $scope.phoneticColour = "#27ae60";
      NProgress.done();
    });
  }

  var getPrediction = function(abstract, category, title) {
    if (name == null || category == null || title == null) {
      return;
    }

    var categories = category.toString().split(', ');

    var publication = {
      title: title,
      abstract: abstract,
      categories: categories
    };

    $http.post("/api/predictor/coreness", publication)
    .success(function(data) {
      $scope.prediction = data.decision;

      if ($scope.prediction == "CORE") {
        $scope.predictionColour = "#27ae60";
      } else if ($scope.prediction == "Non-CORE") {
        $scope.predictionColour = "#d35400";
      } else {
        $scope.predictionColour = "#c0392b";
      }

      NProgress.done();
    });
  }
}]);

app.directive('clusteringResult', function() {
  return {
    restrict: 'E',
    template: '<div ng-bind-html="clusteringHTML"></div>',
    scope: false,
    controller: 'BeardController',
    link: function(scope) {
      // Workaround.
      scope.clusteringHTML = '<h1 class="text-center" ' +
                             'style="color:#7f8c8d;">' +
                             'Idle</h1>';
    }
  };
});

app.directive('predictorResult', function() {
  return {
    restrict: 'E',
    template: '<h1 class="text-center" style="color: ' +
              '{{ predictionColour }} ;">' +
              '{{ prediction }}</h1>',
    scope: false,
    controller: 'BeardController',
    link: function(scope) {
      scope.prediction = "Idle";
      scope.predictionColour = "#7f8c8d";
    }
  };
});

app.directive('phoneticBlock', function() {
  return {
    restrict: 'E',
    template: '<h1 class="text-center" ' +
              'style="color: ' +
              '{{ phoneticColour }} ;">' +
              '{{ phonetic }}</h1>',
    scope: false,
    controller: 'BeardController',
    link: function(scope) {
      scope.phonetic = "Idle";
      scope.phoneticColour = "#7f8c8d";
    }
  };
});
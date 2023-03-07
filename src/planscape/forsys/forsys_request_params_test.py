import json

from base.condition_types import ConditionLevel
from conditions.models import BaseCondition, Condition
from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry
from django.http import HttpRequest, QueryDict
from django.test import TestCase
from forsys.forsys_request_params import (ClusterAlgorithmType,
                                          ClusterAlgorithRequestParams,
                                          ForsysGenerationRequestParams,
                                          ForsysRankingRequestParams)
from plan.models import Plan, Project, ProjectArea
from planscape import settings


class TestClusterAlgorithRequestParams(TestCase):
    def test_reads_default_params(self):
        query_dict = QueryDict('')
        params = ClusterAlgorithRequestParams(query_dict)
        self.assertEqual(params.cluster_algorithm_type,
                         ClusterAlgorithmType.NONE)
        self.assertEqual(params.num_clusters, 500)
        self.assertEqual(params.pixel_index_weight, 0.01)

    def test_reads_cluster_algorithm_type_from_url_params(self):
        query_dict = QueryDict('cluster_algorithm_type=1')
        params = ClusterAlgorithRequestParams(query_dict)
        self.assertEqual(params.cluster_algorithm_type,
                         ClusterAlgorithmType.HIERARCHICAL_IN_PYTHON)

    def test_raises_error_for_bad_cluster_algorithm_type_from_url_params(self):
        query_dict = QueryDict('cluster_algorithm_type=999')
        with self.assertRaises(Exception) as context:
            ClusterAlgorithRequestParams(query_dict)
        self.assertEqual(
            str(context.exception),
            '999 is not a valid ClusterAlgorithmType')

    def test_reads_num_clusters_from_url_params(self):
        query_dict = QueryDict('num_clusters=1125')
        params = ClusterAlgorithRequestParams(query_dict)
        self.assertEqual(params.num_clusters, 1125)

    def test_raises_error_for_bad_num_clusters_from_url_params(self):
        query_dict = QueryDict('num_clusters=-999')
        with self.assertRaises(Exception) as context:
            ClusterAlgorithRequestParams(query_dict)
        self.assertEqual(
            str(context.exception),
            'expected num_clusters to be > 0')

    def test_reads_pixel_index_weight_from_url_params(self):
        query_dict = QueryDict('cluster_pixel_index_weight=0.099')
        params = ClusterAlgorithRequestParams(query_dict)
        self.assertEqual(params.pixel_index_weight, 0.099)

    def test_raises_error_for_bad_pixel_index_weight_from_url_params(
            self):
        query_dict = QueryDict('cluster_pixel_index_weight=-999')
        with self.assertRaises(Exception) as context:
            ClusterAlgorithRequestParams(query_dict)
        self.assertEqual(
            str(context.exception),
            'expected pixel_index_weight to be > 0')


class TestForsysRankingRequestParams(TestCase):
    def test_reads_default_url_params(self):
        qd = QueryDict('set_all_params_via_url_with_default_values=1')
        params = ForsysRankingRequestParams(qd)

        self.assertEqual(params.region, 'sierra_cascade_inyo')
        self.assertEqual(
            params.priorities,
            ['fire_dynamics', 'forest_resilience', 'species_diversity'])
        self.assertEqual(params.priority_weights, [1, 1, 1])

        keys = list(params.project_areas.keys())
        keys.sort()
        self.assertEqual(keys, [1, 2])

        self.assertIsNone(params.max_area_in_km2)
        self.assertIsNone(params.max_cost_in_usd)

        self.assertEqual(params.project_areas[1].coords, (
            (((-120.14015536869722, 39.05413814388948),
              (-120.18409937110482, 39.48622140686506),
              (-119.93422142411087, 39.48622140686506),
              (-119.93422142411087, 39.05413814388948),
              (-120.14015536869722, 39.05413814388948)),),
            (((-120.14015536869722, 38.05413814388948),
              (-120.18409937110482, 38.48622140686506),
              (-119.93422142411087, 38.48622140686506),
              (-119.93422142411087, 38.05413814388948),
              (-120.14015536869722, 38.05413814388948)),))
        )
        self.assertEqual(params.project_areas[1].srid, 4269)
        self.assertEqual(params.project_areas[2].coords, (
            (((-121.14015536869722, 39.05413814388948),
              (-121.18409937110482, 39.48622140686506),
              (-120.53422142411087, 39.48622140686506),
              (-120.53422142411087, 39.05413814388948),
              (-121.14015536869722, 39.05413814388948)),),)
        )
        self.assertEqual(params.project_areas[2].srid, 4269)

    def test_reads_region_from_url_params(self):
        qd = QueryDict(
            'set_all_params_via_url_with_default_values=1&region=foo')
        params = ForsysRankingRequestParams(qd)
        self.assertEqual(params.region, 'foo')

    def test_reads_priorities_from_url_params(self):
        qd = QueryDict(
            'set_all_params_via_url_with_default_values=1' +
            '&priorities=foo&priorities=bar&priorities=baz')
        params = ForsysRankingRequestParams(qd)
        self.assertEqual(params.priorities, ['foo', 'bar', 'baz'])

    def test_reads_priorities_and_weights_from_url_params(self):
        qd = QueryDict(
            'set_all_params_via_url_with_default_values=1' +
            '&priorities=foo&priorities=bar&priorities=baz' +
            '&priority_weights=5.0&priority_weights=2.0&priority_weights=1.0')
        params = ForsysRankingRequestParams(qd)
        self.assertEqual(params.priorities, ['foo', 'bar', 'baz'])
        self.assertListEqual(params.priority_weights, [5, 2, 1])

    def test_raises_error_for_wrong_num_priority_weights_from_url_params(self):
        qd = QueryDict(
            'set_all_params_via_url_with_default_values=1' +
            '&priorities=foo&priorities=bar&priorities=baz' +
            '&priority_weights=5.0&priority_weights=2.0')
        with self.assertRaises(Exception) as context:
            ForsysRankingRequestParams(qd)
        self.assertEqual(
            str(context.exception),
            'expected 3 priority weights, instead, 2 were given')

    def test_reads_max_area_from_url_params(self):
        qd = QueryDict(
            'set_all_params_via_url_with_default_values=1' +
            '&max_area=10000')
        params = ForsysRankingRequestParams(qd)
        self.assertEqual(params.max_area_in_km2, 10000)

    def test_raises_error_on_bad_max_area_from_url_params(self):
        qd = QueryDict(
            'set_all_params_via_url_with_default_values=1' +
            '&max_area=-10')
        with self.assertRaises(Exception) as context:
            ForsysRankingRequestParams(qd)
        self.assertEqual(
            str(context.exception),
            'expected param, max_area, to have a positive value')

    def test_reads_max_cost_from_url_params(self):
        qd = QueryDict(
            'set_all_params_via_url_with_default_values=1' +
            '&max_cost=600')
        params = ForsysRankingRequestParams(qd)
        self.assertEqual(params.max_cost_in_usd, 600)

    def test_raises_error_on_bad_max_cost_from_url_params(self):
        qd = QueryDict(
            'set_all_params_via_url_with_default_values=1' +
            '&max_cost=0')
        with self.assertRaises(Exception) as context:
            ForsysRankingRequestParams(qd)
        self.assertEqual(
            str(context.exception),
            'expected param, max_cost, to have a positive value')

    def test_reads_project_areas_from_url_params(self) -> None:
        qd = QueryDict(
            'set_all_params_via_url_with_default_values=1' +
            '&project_areas={ "id": 1, "srid": 4269, ' +
            '"polygons": [ { "coordinates": [ [-120, 40], [-120, 39], ' +
            '[-119, 39], [-120, 40] ] }, ' +
            '{ "coordinates": [ [-118, 39], [-119, 38], [-119, 39], ' +
            '[-118, 39] ] } ] }' +
            '&project_areas={ "id": 2, "srid": 4269, ' +
            '"polygons": [ { "coordinates": [ [-121, 42], [-120, 40], ' +
            '[-121, 41], [-121, 42] ] } ] }')
        params = ForsysRankingRequestParams(qd)

        keys = list(params.project_areas.keys())
        keys.sort()
        self.assertEqual(keys, [1, 2])

        self.assertEqual(params.project_areas[1].coords, (
            (((-120.0, 40.0),
              (-120.0, 39.0),
              (-119.0, 39.0),
              (-120.0, 40.0)),),
            (((-118.0, 39.0),
              (-119.0, 38.0),
              (-119.0, 39.0),
              (-118.0, 39.0)),))
        )
        self.assertEqual(params.project_areas[1].srid, 4269)
        self.assertEqual(params.project_areas[2].coords, (
            (((-121.0, 42.0), (-120.0, 40.0),
              (-121.0, 41.0), (-121.0, 42.0)),),)
        )
        self.assertEqual(params.project_areas[2].srid, 4269)

    def test_reads_project_areas_from_url_params_with_default_srid(
            self):
        qd = QueryDict(
            'set_all_params_via_url_with_default_values=1' +
            '&project_areas={ "id": 2, ' +
            '"polygons": [ { "coordinates": [ [-121, 42], [-120, 40], ' +
            '[-121, 41], [-121, 42] ] } ] }')
        params = ForsysRankingRequestParams(qd)

        keys = list(params.project_areas.keys())
        keys.sort()
        self.assertEqual(keys, [2])

        self.assertEqual(params.project_areas[2].coords, (
            (((-121.0, 42.0), (-120.0, 40.0),
              (-121.0, 41.0), (-121.0, 42.0)),),)
        )
        self.assertEqual(params.project_areas[2].srid, 4269)

    def test_raises_error_for_url_params_project_areas_w_empty_polygons(
            self):
        qd = QueryDict(
            'set_all_params_via_url_with_default_values=1' +
            '&project_areas={ "id": 1, "srid": 4269, ' +
            '"polygons": [ ] }')
        with self.assertRaises(Exception) as context:
            ForsysRankingRequestParams(qd)
        self.assertEqual(
            str(context.exception),
            'url parameter, project_areas, field, "polygons" is an empty list')

    def test_raises_error_for_invalid_project_areas_from_url_params(
            self):
        qd = QueryDict(
            'set_all_params_via_url_with_default_values=1' +
            '&project_areas={ "id": 1, "srid": 4269, ' +
            '"polygons": [ { "coordinates": [ [-120, 40], [-120, 39] ] } ] }')
        with self.assertRaises(Exception) as context:
            ForsysRankingRequestParams(qd)
        self.assertIn("LinearRing requires at least 4 points, got 2", str(
            context.exception))

    def test_raises_error_for_url_params_project_areas_missing_polygons_field(
            self):
        qd = QueryDict(
            'set_all_params_via_url_with_default_values=1' +
            '&project_areas={ "id": 1, "srid": 4269 }')
        with self.assertRaises(Exception) as context:
            ForsysRankingRequestParams(qd)
        self.assertEquals(
            str(context.exception),
            'url parameter, project_areas, missing field, "polygons"')

    def test_raises_error_for_url_params_project_areas_missing_id_field(
            self):
        qd = QueryDict(
            'set_all_params_via_url_with_default_values=1' +
            '&project_areas={ "srid": 4269, ' +
            '"polygons": [ { "coordinates": [ [-120, 40], [-120, 39], ' +
            '[-119, 39], [-120, 40] ] }, ' +
            '{ "coordinates": [ [-118, 39], [-119, 38], [-119, 39], ' +
            '[-118, 39] ] } ] }' +
            '&project_areas={ "id": 2, "srid": 4269, ' +
            '"polygons": [ { "coordinates": [ [-121, 42], [-120, 40], ' +
            '[-121, 41], [-121, 42] ] } ] }')
        with self.assertRaises(Exception) as context:
            ForsysRankingRequestParams(qd)
        self.assertEquals(
            str(context.exception),
            'url params, project_areas, missing field, "id"')


class TestForsysRankingRequestParams_ReadFromDb(TestCase):
    def setUp(self) -> None:
        self.base_condition1 = BaseCondition.objects.create(
            condition_name="name1", condition_level=ConditionLevel.ELEMENT)
        self.base_condition2 = BaseCondition.objects.create(
            condition_name="name2", condition_level=ConditionLevel.ELEMENT)
        self.condition1 = Condition.objects.create(
            condition_dataset=self.base_condition1, raster_name="name1")
        self.condition2 = Condition.objects.create(
            condition_dataset=self.base_condition2, raster_name="name2")

        self.user = User.objects.create(username='testuser')
        self.user.set_password('12345')
        self.user.save()

        self.geometry = {'type': 'MultiPolygon',
                         'coordinates': [[[[1, 2], [2, 3], [3, 4], [1, 2]]]]}
        self.stored_geometry = GEOSGeometry(json.dumps(self.geometry))
        self.plan_with_user = Plan.objects.create(
            owner=self.user, name="plan", region_name='sierra_cascade_inyo',
            geometry=self.stored_geometry)

        self.project_with_user = Project.objects.create(
            owner=self.user, plan=self.plan_with_user, max_budget=100, )
        self.project_with_user.priorities.add(self.condition1)
        self.project_with_user.priorities.add(self.condition2)

        self.project_area_with_user = ProjectArea.objects.create(
            owner=self.user, project=self.project_with_user,
            project_area=self.stored_geometry, estimated_area_treated=200)

    def test_missing_project_id(self):
        qd = QueryDict('')
        self.assertRaises(Exception, ForsysRankingRequestParams, qd)

    def test_nonexistent_project_id(self):
        qd = QueryDict('project_id=10')
        self.assertRaises(Exception, ForsysRankingRequestParams, qd)

    def test_empty_project_areas(self):
        self.project_area_with_user.delete()
        qd = QueryDict('project_id=' + str(self.project_with_user.pk))
        params = ForsysRankingRequestParams(qd)
        self.assertEqual(params.region, 'sierra_cascade_inyo')
        self.assertEqual(len(params.project_areas), 0)

    def test_read_ok(self):
        qd = QueryDict('project_id=' + str(self.project_with_user.pk))
        params = ForsysRankingRequestParams(qd)
        self.assertEqual(params.region, 'sierra_cascade_inyo')
        self.assertEqual(len(params.project_areas), 1)
        self.assertTrue(
            params.project_areas[self.project_area_with_user.pk].equals(
                self.stored_geometry))
        self.assertEqual(params.priorities, ["name1", "name2"])


class TestForsysGenerationRequestParams(TestCase):
    def test_reads_default_url_params(self):
        request = HttpRequest()
        request.GET = QueryDict(
            'set_all_params_via_url_with_default_values=1')
        params = ForsysGenerationRequestParams(request)

        self.assertEqual(params.region, 'sierra_cascade_inyo')
        self.assertEqual(
            params.priorities,
            ['fire_dynamics', 'forest_resilience', 'species_diversity'])
        self.assertEqual(params.priority_weights, [1, 1, 1])

        self.assertEqual(params.planning_area.coords, (
            (((-120.14015536869722, 39.05413814388948),
              (-120.18409937110482, 39.48622140686506),
              (-119.93422142411087, 39.48622140686506),
              (-119.93422142411087, 39.05413814388948),
              (-120.14015536869722, 39.05413814388948)),),
            (((-120.14015536869722, 38.05413814388948),
              (-120.18409937110482, 38.48622140686506),
              (-119.93422142411087, 38.48622140686506),
              (-119.93422142411087, 38.05413814388948),
              (-120.14015536869722, 38.05413814388948)),))
        )
        self.assertEqual(params.planning_area.srid, 4269)
        self.assertEqual(params.cluster_params.cluster_algorithm_type,
                         ClusterAlgorithmType.NONE)
        self.assertEqual(params.cluster_params.num_clusters, 500)
        self.assertEqual(
            params.cluster_params.pixel_index_weight, 0.01)

    def test_reads_region_from_url_params(self):
        request = HttpRequest()
        request.GET = QueryDict(
            'set_all_params_via_url_with_default_values=1&region=foo')
        params = ForsysGenerationRequestParams(request)
        self.assertEqual(params.region, 'foo')

    def test_reads_priorities_from_url_params(self):
        request = HttpRequest()
        request.GET = QueryDict(
            'set_all_params_via_url_with_default_values=1' +
            '&priorities=foo&priorities=bar&priorities=baz')
        params = ForsysGenerationRequestParams(request)
        self.assertEqual(params.priorities, ['foo', 'bar', 'baz'])

    def test_reads_priorities_and_weights_from_url_params(self):
        request = HttpRequest()
        request.GET = QueryDict(
            'set_all_params_via_url_with_default_values=1' +
            '&priorities=foo&priorities=bar&priorities=baz' +
            '&priority_weights=5.0&priority_weights=2.0&priority_weights=1.0')
        params = ForsysGenerationRequestParams(request)
        self.assertEqual(params.priorities, ['foo', 'bar', 'baz'])
        self.assertListEqual(params.priority_weights, [5, 2, 1])

    def test_raises_error_for_wrong_num_priority_weights_from_url_params(self):
        request = HttpRequest()
        request.GET = QueryDict(
            'set_all_params_via_url_with_default_values=1' +
            '&priorities=foo&priorities=bar&priorities=baz' +
            '&priority_weights=5.0&priority_weights=2.0')
        with self.assertRaises(Exception) as context:
            ForsysGenerationRequestParams(request)
        self.assertEqual(
            str(context.exception),
            'expected 3 priority weights, instead, 2 were given')

    def test_reads_planning_area_from_url_params(self) -> None:
        request = HttpRequest()
        request.GET = QueryDict(
            'set_all_params_via_url_with_default_values=1' +
            '&planning_area={ "id": 1, "srid": 4269, ' +
            '"polygons": [ { "coordinates": [ [-120, 40], [-120, 39], ' +
            '[-119, 39], [-120, 40] ] }, ' +
            '{ "coordinates": [ [-118, 39], [-119, 38], [-119, 39], ' +
            '[-118, 39] ] } ] }')
        params = ForsysGenerationRequestParams(request)

        self.assertEqual(params.planning_area.coords, (
            (((-120.0, 40.0),
              (-120.0, 39.0),
              (-119.0, 39.0),
              (-120.0, 40.0)),),
            (((-118.0, 39.0),
              (-119.0, 38.0),
              (-119.0, 39.0),
              (-118.0, 39.0)),))
        )
        self.assertEqual(params.planning_area.srid, 4269)

    def test_reads_planning_area_from_url_params_with_default_srid(
            self):
        request = HttpRequest()
        request.GET = QueryDict(
            'set_all_params_via_url_with_default_values=1' +
            '&planning_area={ "id": 2, ' +
            '"polygons": [ { "coordinates": [ [-121, 42], [-120, 40], ' +
            '[-121, 41], [-121, 42] ] } ] }')
        params = ForsysGenerationRequestParams(request)

        self.assertEqual(params.planning_area.coords, (
            (((-121.0, 42.0), (-120.0, 40.0),
              (-121.0, 41.0), (-121.0, 42.0)),),)
        )
        self.assertEqual(params.planning_area.srid, 4269)

    def test_raises_error_for_url_params_planning_area_w_empty_polygons(
            self):
        request = HttpRequest()
        request.GET = QueryDict(
            'set_all_params_via_url_with_default_values=1' +
            '&planning_area={ "id": 1, "srid": 4269, ' +
            '"polygons": [ ] }')
        with self.assertRaises(Exception) as context:
            ForsysGenerationRequestParams(request)
        self.assertEqual(
            str(context.exception),
            'url parameter, planning_area, field, "polygons" is an empty list')

    def test_raises_error_for_invalid_planning_area_from_url_params(
            self):
        request = HttpRequest()
        request.GET = QueryDict(
            'set_all_params_via_url_with_default_values=1' +
            '&planning_area={ "id": 1, "srid": 4269, ' +
            '"polygons": [ { "coordinates": [ [-120, 40], [-120, 39] ] } ] }')
        with self.assertRaises(Exception) as context:
            ForsysGenerationRequestParams(request)
        self.assertIn("LinearRing requires at least 4 points, got 2", str(
            context.exception))

    def test_raises_error_for_url_params_planning_area_missing_polygons_field(
            self):
        request = HttpRequest()
        request.GET = QueryDict(
            'set_all_params_via_url_with_default_values=1' +
            '&planning_area={ "id": 1, "srid": 4269 }')
        with self.assertRaises(Exception) as context:
            ForsysGenerationRequestParams(request)
        self.assertEquals(
            str(context.exception),
            'url parameter, planning_area, missing field, "polygons"')

    def test_raises_error_for_url_params_planning_area_missing_id_field(
            self):
        request = HttpRequest()
        request.GET = QueryDict(
            'set_all_params_via_url_with_default_values=1' +
            '&planning_area={ "srid": 4269, ' +
            '"polygons": [ { "coordinates": [ [-120, 40], [-120, 39], ' +
            '[-119, 39], [-120, 40] ] }, ' +
            '{ "coordinates": [ [-118, 39], [-119, 38], [-119, 39], ' +
            '[-118, 39] ] } ] }')
        with self.assertRaises(Exception) as context:
            ForsysGenerationRequestParams(request)
        self.assertEquals(
            str(context.exception),
            'url params, planning_area, missing field, "id"')


class TestForsysGenerationRequestParams_ReadFromDb(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(username='testuser')
        self.user.set_password('12345')
        self.user.save()

        self.geometry = {'type': 'MultiPolygon',
                         'coordinates': [[[[1, 2], [2, 3], [3, 4], [1, 2]]]]}
        self.stored_geometry = GEOSGeometry(json.dumps(self.geometry))
        self.plan_with_user = Plan.objects.create(
            owner=self.user, name="plan", region_name='sierra_cascade_inyo',
            geometry=self.stored_geometry)

    def test_read_ok(self):
        request = HttpRequest()
        request.GET = QueryDict('id=' + str(self.plan_with_user.pk))
        request.user = self.user
        params = ForsysGenerationRequestParams(request)
        self.assertEqual(params.region, 'sierra_cascade_inyo')
        self.assertEqual(params.planning_area.coords, ((
            ((1.0, 2.0), (2.0, 3.0), (3.0, 4.0), (1.0, 2.0)),),))
        self.assertEqual(params.cluster_params.cluster_algorithm_type,
                         ClusterAlgorithmType.NONE)
        self.assertEqual(params.cluster_params.num_clusters, 500)
        self.assertEqual(
            params.cluster_params.pixel_index_weight, 0.01)

    def test_fails_on_no_user(self):
        request = HttpRequest()
        request.GET = QueryDict('id=' + str(self.plan_with_user.pk))
        with self.assertRaises(Exception) as context:
            ForsysGenerationRequestParams(request)
        self.assertEquals(
            str(context.exception),
            "'HttpRequest' object has no attribute 'user'")

    def test_fails_on_wrong_user(self):
        wrong_user = User.objects.create(username='wrong_user')
        wrong_user.set_password('12345')
        wrong_user.save()

        request = HttpRequest()
        request.GET = QueryDict('id=' + str(self.plan_with_user.pk))
        request.user = wrong_user
        with self.assertRaises(Exception) as context:
            ForsysGenerationRequestParams(request)
        self.assertEquals(
            str(context.exception),
            "You do not have permission to view this plan.")

    def test_fails_no_plan(self):
        request = HttpRequest()
        request.GET = QueryDict()
        request.user = self.user
        with self.assertRaises(Exception) as context:
            ForsysGenerationRequestParams(request)
        self.assertEquals(str(context.exception), "'id'")

    def test_fails_nonexistent_plan_id(self):
        request = HttpRequest()
        request.GET = QueryDict('id=' + str(125125))
        request.user = self.user
        with self.assertRaises(Exception) as context:
            ForsysGenerationRequestParams(request)
        self.assertEquals(
            str(context.exception),
            "Plan matching query does not exist.")

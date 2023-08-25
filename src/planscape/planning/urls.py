from django.conf.urls import include
from django.urls import path
from planning.views import (create_planning_area, delete_planning_area,
                            get_planning_area_by_id, list_planning_areas,
                            update_planning_area,
                            create_scenario, delete_scenario, get_scenario_by_id,
                            list_scenarios_for_planning_area, update_scenario,
                            update_scenario_result)

app_name = 'planning'

#TODO: Change these to more standardized id-driven APIs, e.g. scenarios/[id]

urlpatterns = [
    # Auto-generated API documentation
    path('admin/doc/', include('django.contrib.admindocs.urls')),

    # Plans / Planning Areas
    path('create_planning_area/', create_planning_area, name='create_planning_area'),
    path('delete_planning_area/', delete_planning_area, name='delete_planning_area'),
    path('get_planning_area_by_id/', get_planning_area_by_id, name='get_planning_area_by_id'),
    path('list_planning_areas/', list_planning_areas, name='list_planning_areas'),
    path('update_planning_area/', update_planning_area, name='update_planning_area'),

    # Scenarios
    path('create_scenario/', create_scenario, name='create_scenario'),
    path('delete_scenario/', delete_scenario, name='delete_scenario'),
    path('get_scenario_by_id/', get_scenario_by_id, name='get_scenario_by_id'),
    path('list_scenarios_for_planning_area/', list_scenarios_for_planning_area, name='list_scenarios_for_planning_area'),
    path('update_scenario/', update_scenario, name='update_scenario'),
    path('update_scenario_result/', update_scenario_result, name='update_scenario_result'),

    # Project Areas
    # TODO
]
import rpy2

import numpy as np

from typing import TypedDict


class RankedProject(TypedDict):
    # Project ID.
    id: int
    # Contribution of each priority to the total score.
    # Contribution is priority weight * priority impact.
    weighted_priority_scores: dict[str, float]
    # The total score, summed across weighted priority scores.
    total_score: float
    # Project rank.
    rank: int


class Scenario(TypedDict):
    # Priority weights for the scenario.
    priority_weights: dict[str, float]
    # A list of the projects, ranked according to a weighted sum of benefit/AP
    # scores with the highest scoring at index 0.
    ranked_projects: list[RankedProject]
    # Given ranked projects, a cumulative sum of project area.
    cumulative_ranked_project_area: list[float]
    # Given ranked projects, a cumulative sum of project cost.
    cumulative_ranked_project_cost: list[float]


# Transforms the output of a Forsys scenario set run into a more
# easily-interpreted version.
class ForsysScenarioSetOutput():
    # The raw forsys output consists of 3 R dataframes. This is the index of
    # the "project output" dataframe.
    _PROJECT_OUTPUT_INDEX = 1

    # ---------------------------
    # string patterns for headers
    # ---------------------------
    # The priority weight header in the "project output" dataframe.
    _PRIORITY_WEIGHT_STRFORMAT = "Pr_%d_%s"
    # The priority contribution header in the "project output" dataframe.
    # Weighted priority score is priority weight * priority contribution.
    _CONTRIBUTION_STRFORMAT = "ETrt_%s"
    # The project area rank header in the "project output" dataframe.
    _TREATMENT_RANK_HEADER = "treatment_rank"

    # This is for converting a (priority, weight) pair into a string.
    _WEIGHT_STRFORMAT = "%s:%d"

    # A dictionary of the forsys output, organized by scenario. The key is a
    # list of "<priority>:<weight>" pairs separated by spaces.
    scenarios: dict[str, Scenario]

    # The "project output" dataframe is converted into a dictionary of lists so
    # that it's easier to parse.
    _forsys_output_df: dict[str, list]
    # The conditions to be prioritized.
    _priorities: list[str]
    # The headers used to parse the "project output" dataframe.
    _priority_weight_headers: list[str]
    _priority_contribution_headers: list[str]
    _project_id_header: str
    _area_contribution_header: str
    _cost_contribution_header: str

    # Initializes a ForsysScenarioSetOutput instance given raw forsys output
    # and the following inputs to the forsys call: header names, list of
    # priorities.
    # Of note, priorities must be listed in the same format and order they're
    # listed for the forsys call.
    def __init__(
            self, raw_forsys_output: "rpy2.robjects.vectors.ListVector",
            priorities: list[str],
            project_id_header: str, area_header: str, cost_header: str):
        self._save_raw_forsys_output_as_dict(raw_forsys_output)

        self._set_header_names(priorities, area_header,
                               cost_header, project_id_header)

        self.scenarios = {}
        for i in range(len(self._forsys_output_df[project_id_header])):
            scenario_weights, scenario_str = self._get_scenario(i)

            if scenario_str in self.scenarios.keys():
                self._append_ranked_project_to_existing_scenario(
                    scenario_str, scenario_weights, i)
            else:
                self._append_ranked_project_to_new_scenario(
                    scenario_str, scenario_weights, i)

    def _save_raw_forsys_output_as_dict(
            self, raw_forsys_output: "rpy2.robjects.vectors.DataFrame") -> None:
        rdf = raw_forsys_output[self._PROJECT_OUTPUT_INDEX]
        self._forsys_output_df = {
            key: np.asarray(rdf.rx2(key)) for key in rdf.names}

    def _check_header_name(self, header) -> None:
        if header not in self._forsys_output_df.keys():
            raise Exception(
                "header, %s, is not a forsys output header" % header)

    def _set_header_names(
            self, priorities: list[str],
            area_header: str, cost_header: str, project_id_header: str) -> None:
        self._priorities = priorities
        self._priority_weight_headers = [self._PRIORITY_WEIGHT_STRFORMAT % (
            i+1, priorities[i]) for i in range(len(priorities))]
        for h in self._priority_weight_headers:
            self._check_header_name(h)

        self._priority_contribution_headers = [
            self._CONTRIBUTION_STRFORMAT % (p) for p in priorities]
        for h in self._priority_contribution_headers:
            self._check_header_name(h)
        self._area_contribution_header = self._CONTRIBUTION_STRFORMAT % area_header
        self._check_header_name(self._area_contribution_header)
        self._cost_contribution_header = self._CONTRIBUTION_STRFORMAT % cost_header
        self._check_header_name(self._cost_contribution_header)
        self._project_id_header = project_id_header
        self._check_header_name(self._project_id_header)

    def _get_weights_str(self, weights: dict) -> str:
        return " ".join([self._WEIGHT_STRFORMAT % (k, weights[k])
                         for k in weights.keys()])

    def _get_scenario(self, ind: int) -> tuple[dict, str]:
        weights = {
            self._priorities[i]: int(self._forsys_output_df[
                self._priority_weight_headers[i]][ind])
            for i in range(len(self._priorities))
        }
        return weights, self._get_weights_str(weights)

    def _create_ranked_project(
            self, scenario_weights: dict, ind: int) -> RankedProject:
        project: RankedProject = {
            'id': int(
                self._forsys_output_df[self._project_id_header][ind]),
            'weighted_priority_scores': {},
            'rank': int(
                self._forsys_output_df[self._TREATMENT_RANK_HEADER][ind]),
            'total_score': 0,
        }
        for i in range(len(self._priorities)):
            p = self._priorities[i]
            contribution = self._forsys_output_df[
                self._priority_contribution_headers[i]
            ][ind] * scenario_weights[p]
            project['weighted_priority_scores'][p] = contribution
            project['total_score'] = project['total_score'] + contribution
        return project

    def _append_ranked_project_to_existing_scenario(
            self, scenario_str: str, scenario_weights: dict, i: int) -> None:
        scenario = self.scenarios[scenario_str]
        ranked_projects = scenario['ranked_projects']
        scenario_ind = len(ranked_projects)
        ranked_projects.append(self._create_ranked_project(
            scenario_weights, i))
        scenario['cumulative_ranked_project_area'].append(
            scenario['cumulative_ranked_project_area'][scenario_ind - 1] + self.
            _forsys_output_df[self._area_contribution_header][i])
        scenario['cumulative_ranked_project_cost'].append(
            scenario['cumulative_ranked_project_cost'][scenario_ind - 1] + self.
            _forsys_output_df[self._cost_contribution_header][i])

    def _append_ranked_project_to_new_scenario(
            self, scenario_str: str, scenario_weights: dict, i: int) -> None:
        scenario: Scenario = {
            'priority_weights': scenario_weights,
            'ranked_projects': [self._create_ranked_project(
                scenario_weights, i)],
            'cumulative_ranked_project_area': [
                self._forsys_output_df[self._area_contribution_header][i]
            ],
            'cumulative_ranked_project_cost': [
                self._forsys_output_df[self._cost_contribution_header][i]
            ],
        }
        self.scenarios[scenario_str] = scenario


# Transforms the output of a Forsys scenario run into a more
# easily-interpreted version.
class ForsysScenarioOutput():
    # The raw forsys output consists of 3 R dataframes. This is the index of
    # the "project output" dataframe.
    _PROJECT_OUTPUT_INDEX = 1

    # ---------------------------
    # string patterns for headers
    # ---------------------------
    # The project-level treatment impact header format in the forsys "project
    # output" dataframe. Recall:
    # - Treatment impact for a project is the sum of the treatment impacts of
    # individual stands [selected for treatment given global constraints].
    # - Treatment impact of individual stands is specified as part of the forsys
    # input dataframe.
    _CONTRIBUTION_STRFORMAT = "ETrt_%s"
    # The project area rank header in the "project output" dataframe.
    _TREATMENT_RANK_HEADER = "treatment_rank"

    # This is for converting a (priority, weight) pair into a string.
    _WEIGHT_STRFORMAT = "%s:%d"

    # The parsed scenario.
    scenario: Scenario

    # The raw forsys output consists of 3 R dataframes.
    # The "project output" dataframe is converted into a dictionary of lists so
    # that it's easier to process in Python.
    _forsys_output_df: dict[str, list]
    # The conditions to be prioritized.
    # This represents the keys of constructor input parameter, priority_weights.
    _priorities: list[str]
    # The headers used to parse the "project output" dataframe.
    _priority_contribution_headers: list[str]
    _project_id_header: str
    _area_contribution_header: str
    _cost_contribution_header: str

    # Initializes a ForsysScenarioOutput instance given raw forsys output
    # and the following inputs to the forsys call: header names, list of
    # priorities.
    # Of note, priorities must be listed in the same format and order they're
    # listed for the forsys call.
    def __init__(self, raw_forsys_output: "rpy2.robjects.vectors.ListVector",
                 priority_weights: dict[str, float],
                 project_id_header: str, area_header: str, cost_header: str):
        self._save_raw_forsys_output_as_dict(raw_forsys_output)

        self._set_header_names(list(priority_weights.keys()), area_header,
                               cost_header, project_id_header)

        self.scenario = Scenario(
            {'priority_weights': priority_weights, 'ranked_projects': [],
             'cumulative_ranked_project_area': [],
             'cumulative_ranked_project_cost': []})
        for i in range(len(self._forsys_output_df[project_id_header])):
            self._append_ranked_project_to_scenario(i)

    def _save_raw_forsys_output_as_dict(
            self, raw_forsys_output: "rpy2.robjects.vectors.DataFrame") -> None:
        rdf = raw_forsys_output[self._PROJECT_OUTPUT_INDEX]
        self._forsys_output_df = {
            key: np.asarray(rdf.rx2(key)) for key in rdf.names}

    def _check_header_name(self, header) -> None:
        if header not in self._forsys_output_df.keys():
            raise Exception(
                "header, %s, is not a forsys output header" % header)

    def _set_header_names(
            self, priorities: list[str],
            area_header: str, cost_header: str, project_id_header: str) -> None:
        self._priorities = priorities

        self._priority_contribution_headers = [
            self._CONTRIBUTION_STRFORMAT % (p) for p in priorities]
        for p in self._priority_contribution_headers:
            self._check_header_name(p)
        self._area_contribution_header = self._CONTRIBUTION_STRFORMAT % area_header
        self._check_header_name(self._area_contribution_header)
        self._cost_contribution_header = self._CONTRIBUTION_STRFORMAT % cost_header
        self._check_header_name(self._cost_contribution_header)
        self._project_id_header = project_id_header
        self._check_header_name(self._project_id_header)

    def _create_ranked_project(
            self, scenario_weights: dict[str, float],
            ind: int) -> RankedProject:
        project: RankedProject = {
            'id': int(
                self._forsys_output_df[self._project_id_header][ind]),
            'weighted_priority_scores': {},
            'rank': int(
                self._forsys_output_df[self._TREATMENT_RANK_HEADER][ind]),
            'total_score': 0,
        }
        for i in range(len(self._priorities)):
            p = self._priorities[i]
            contribution = self._forsys_output_df[
                self._priority_contribution_headers[i]
            ][ind] * scenario_weights[p]
            project['weighted_priority_scores'][p] = contribution
            project['total_score'] = project['total_score'] + contribution
        return project

    def _append_ranked_project_to_scenario(self, i: int) -> None:
        ranked_projects = self.scenario['ranked_projects']
        scenario_ind = len(ranked_projects)
        ranked_projects.append(self._create_ranked_project(
            self.scenario['priority_weights'], i))
        if scenario_ind == 0:
            self.scenario['cumulative_ranked_project_area'].append(
                self._forsys_output_df[self._area_contribution_header][i])
            self.scenario['cumulative_ranked_project_cost'].append(
                self._forsys_output_df[self._cost_contribution_header][i])
        else:
            self.scenario['cumulative_ranked_project_area'].append(
                self.scenario['cumulative_ranked_project_area']
                [scenario_ind - 1] + self._forsys_output_df
                [self._area_contribution_header][i])
            self.scenario['cumulative_ranked_project_cost'].append(
                self.scenario['cumulative_ranked_project_cost']
                [scenario_ind - 1] + self._forsys_output_df
                [self._cost_contribution_header][i])

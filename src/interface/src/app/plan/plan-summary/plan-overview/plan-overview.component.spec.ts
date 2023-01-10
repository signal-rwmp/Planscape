import { PlanModule } from './../../plan.module';
import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PlanOverviewComponent } from './plan-overview.component';

describe('PlanOverviewComponent', () => {
  let component: PlanOverviewComponent;
  let fixture: ComponentFixture<PlanOverviewComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PlanModule],
      declarations: [PlanOverviewComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(PlanOverviewComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('createScenario should emit event', () => {
    spyOn(component.createScenarioEvent, 'emit');

    component.createScenario();

    expect(component.createScenarioEvent.emit).toHaveBeenCalled();
  });
});

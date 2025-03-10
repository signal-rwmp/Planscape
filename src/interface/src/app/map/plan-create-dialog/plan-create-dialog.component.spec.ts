import { NO_ERRORS_SCHEMA } from '@angular/core';
import {
  ComponentFixture,
  fakeAsync,
  TestBed,
  tick,
} from '@angular/core/testing';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';

import { PlanCreateDialogComponent } from './plan-create-dialog.component';
import { ReactiveFormsModule } from '@angular/forms';
import { By } from '@angular/platform-browser';
import { PlanService, SessionService } from '../../services';
import { BehaviorSubject, of } from 'rxjs';
import { MaterialModule } from '../../material/material.module';
import { DialogModule } from '@angular/cdk/dialog';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { Region } from '../../types';

describe('PlanCreateDialogComponent', () => {
  let component: PlanCreateDialogComponent;
  let fixture: ComponentFixture<PlanCreateDialogComponent>;
  const fakeGeoJson: GeoJSON.GeoJSON = {
    type: 'FeatureCollection',
    features: [
      {
        type: 'Feature',
        geometry: {
          type: 'MultiPolygon',
          coordinates: [
            [
              [
                [10, 20],
                [10, 30],
                [15, 15],
              ],
            ],
          ],
        },
        properties: {
          shape_name: 'Test',
        },
      },
    ],
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        ReactiveFormsModule,
        MaterialModule,
        DialogModule,
        NoopAnimationsModule,
      ],
      declarations: [PlanCreateDialogComponent],
      providers: [
        {
          provide: PlanService,
          useValue: {
            planNameExists: () => of(false),
            createPlan: () => new BehaviorSubject({ result: { id: 'planId' } }),
          },
        },
        {
          provide: MatDialogRef,
          useValue: {
            close: () => {},
          },
        },
        {
          provide: MAT_DIALOG_DATA,
          useValue: { shape: fakeGeoJson },
        },
        {
          provide: SessionService,
          useValue: { region$: new BehaviorSubject(Region.SIERRA_NEVADA) },
        },
      ],
      schemas: [NO_ERRORS_SCHEMA],
    }).compileComponents();

    fixture = TestBed.createComponent(PlanCreateDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should submit if there is a plan name', fakeAsync(() => {
    const dialogRef = TestBed.inject(MatDialogRef<PlanCreateDialogComponent>);
    spyOn(dialogRef, 'close');
    component.planForm.setValue({
      planName: 'some plan',
    });

    const saveBtn = fixture.debugElement.query(
      By.css('[data-id="save"]')
    ).nativeElement;
    saveBtn.click();
    tick();
    expect(dialogRef.close).toHaveBeenCalledTimes(1);
  }));
  it('should not submit if there is not a plan name', () => {
    const dialogRef = TestBed.inject(MatDialogRef<PlanCreateDialogComponent>);
    spyOn(dialogRef, 'close');

    const saveBtn = fixture.debugElement.query(
      By.css('[data-id="save"]')
    ).nativeElement;
    saveBtn.click();
    expect(dialogRef.close).not.toHaveBeenCalled();
  });

  it('should not submit if a plan already has the same name', () => {
    const dialogRef = TestBed.inject(MatDialogRef<PlanCreateDialogComponent>);
    spyOn(dialogRef, 'close');
    const service = TestBed.inject(PlanService);
    spyOn(service, 'planNameExists').and.returnValue(of(true));

    const saveBtn = fixture.debugElement.query(
      By.css('[data-id="save"]')
    ).nativeElement;
    saveBtn.click();
    expect(dialogRef.close).not.toHaveBeenCalled();
  });

  it('should save plan', fakeAsync(() => {
    const dialogRef = TestBed.inject(MatDialogRef<PlanCreateDialogComponent>);
    spyOn(dialogRef, 'close');
    component.planForm.setValue({
      planName: 'some plan',
    });
    const planService = TestBed.inject(PlanService);
    spyOn(planService, 'createPlan').and.callThrough();

    const saveBtn = fixture.debugElement.query(
      By.css('[data-id="save"]')
    ).nativeElement;
    saveBtn.click();
    tick();
    expect(planService.createPlan).toHaveBeenCalledWith({
      name: 'some plan',
      region: Region.SIERRA_NEVADA,
      planningArea: fakeGeoJson,
    });
  }));
});

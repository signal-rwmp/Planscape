import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { MatDialog } from '@angular/material/dialog';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { Router } from '@angular/router';
import { BehaviorSubject, of } from 'rxjs';
import { MaterialModule } from 'src/app/material/material.module';
import { PlanPreview, Region } from 'src/app/types';

import { AuthService } from '../../services/auth.service';
import { PlanService } from '../../services/plan.service';
import { PlanTableComponent } from './plan-table.component';
import { DeleteDialogComponent } from '../../delete-dialog/delete-dialog.component';

describe('PlanTableComponent', () => {
  const fakePlan1: PlanPreview = {
    id: 1,
    name: 'somePlan',
    region: Region.SIERRA_NEVADA,
    lastUpdated: new Date(),
    notes: '',
    scenarios: 1,
    ownerId: 1,
  };
  const fakePlan2: PlanPreview = {
    id: 2,
    name: 'somePlan',
    region: Region.SIERRA_NEVADA,
    lastUpdated: new Date(),
    notes: '',
    scenarios: 2,
    ownerId: 1,
  };

  let component: PlanTableComponent;
  let fixture: ComponentFixture<PlanTableComponent>;
  let fakeAuthService: AuthService;
  let loggedInStatus$: BehaviorSubject<boolean>;
  let fakePlanService: PlanService;
  let routerStub = () => ({ navigate: (array: string[]) => ({}) });

  beforeEach(async () => {
    loggedInStatus$ = new BehaviorSubject(false);
    fakeAuthService = jasmine.createSpyObj(
      'AuthService',
      {},
      {
        isLoggedIn$: loggedInStatus$,
      }
    );
    fakePlanService = jasmine.createSpyObj('PlanService', {
      deletePlan: of('1'),
      listPlansByUser: of([fakePlan1, fakePlan2]),
    });

    await TestBed.configureTestingModule({
      imports: [
        BrowserAnimationsModule,
        FormsModule,
        MaterialModule,
        ReactiveFormsModule,
      ],
      declarations: [PlanTableComponent],
      providers: [
        {
          provide: AuthService,
          useValue: fakeAuthService,
        },
        { provide: PlanService, useValue: fakePlanService },
        { provide: Router, useFactory: routerStub },
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(PlanTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('refresh', () => {
    it('should fetch plans from the DB', () => {
      component.refresh();
      expect(fakePlanService.listPlansByUser).toHaveBeenCalledTimes(3);
      expect(component.datasource.data).toEqual([
        {
          ...fakePlan1,
          totalAcres: 0,
        },
        {
          ...fakePlan2,
          totalAcres: 0,
        },
      ]);
    });
  });

  describe('delete', () => {
    it('should open a dialog with a single ID to delete', () => {
      const dialogSpy: MatDialog = fixture.debugElement.injector.get(MatDialog);
      spyOn(dialogSpy, 'open').and.callThrough();
      component.selectedPlan = { ...fakePlan1, totalAcres: 100 };
      component.deletePlan();

      expect(dialogSpy.open).toHaveBeenCalledOnceWith(DeleteDialogComponent, {
        data: { name: '"somePlan"' },
      });
    });
  });

  it('when logged in status changes, refresh plans', () => {
    expect(fakePlanService.listPlansByUser).toHaveBeenCalledTimes(2);

    loggedInStatus$.next(true);

    expect(fakePlanService.listPlansByUser).toHaveBeenCalledTimes(3);
  });
});

import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SummaryPanelComponent } from './summary-panel.component';
import { CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';

describe('SummaryPanelComponent', () => {
  let component: SummaryPanelComponent;
  let fixture: ComponentFixture<SummaryPanelComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [SummaryPanelComponent],
      schemas: [CUSTOM_ELEMENTS_SCHEMA],
    }).compileComponents();

    fixture = TestBed.createComponent(SummaryPanelComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

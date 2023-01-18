import { HttpClientTestingModule } from '@angular/common/http/testing';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { of } from 'rxjs';
import { colormapConfigToLegend } from 'src/app/types';

import { MapService } from './../../../services/map.service';
import { ColormapConfig } from './../../../types/legend.types';
import { CreateScenariosIntroComponent } from './create-scenarios-intro.component';

describe('CreateScenariosIntroComponent', () => {
  let component: CreateScenariosIntroComponent;
  let fixture: ComponentFixture<CreateScenariosIntroComponent>;
  let fakeMapService: MapService;

  const fakeColormapConfig: ColormapConfig = {
    name: 'fakecolormap',
    values: [
      {
        rgb: '#000000',
        name: 'fakelabel',
      },
    ],
  };

  beforeEach(async () => {
    fakeMapService = jasmine.createSpyObj('MapService', {
      getColormap: of(fakeColormapConfig),
    });
    await TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      declarations: [CreateScenariosIntroComponent],
      providers: [{ provide: MapService, useValue: fakeMapService }],
    }).compileComponents();

    fixture = TestBed.createComponent(CreateScenariosIntroComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should fetch colormap from service to create legend', () => {
    expect(fakeMapService.getColormap).toHaveBeenCalledOnceWith('viridis');
    expect(component.legend).toEqual(
      colormapConfigToLegend(fakeColormapConfig)
    );
  });
});
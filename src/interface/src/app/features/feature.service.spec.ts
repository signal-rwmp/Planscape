import { TestBed } from '@angular/core/testing';

import { FeatureService } from './feature.service';
import { FeaturesModule } from './features.module';

describe('FeatureService', () => {
  let service: FeatureService;

  beforeEach(() => {
    TestBed.configureTestingModule({ imports: [FeaturesModule] });
    service = TestBed.inject(FeatureService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('false flag should be false', () => {
    expect(service.isFeatureEnabled('testFalseFeature')).toBeFalse();
  });

  it('true flag should be true', () => {
    expect(service.isFeatureEnabled('testTrueFeature')).toBeTrue();
  });

  it('nonexistent flag should be false', () => {
    expect(service.isFeatureEnabled('nonexistent_flag')).toBeFalse();
  });
});

import { TestBed } from '@angular/core/testing';

import { NavgationService } from './navgation.service';

describe('NavgationService', () => {
  let service: NavgationService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(NavgationService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

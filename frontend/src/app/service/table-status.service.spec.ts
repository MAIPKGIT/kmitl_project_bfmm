import { TestBed } from '@angular/core/testing';

import { TableStatusService } from './table-status.service';

describe('TableStatusService', () => {
  let service: TableStatusService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(TableStatusService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

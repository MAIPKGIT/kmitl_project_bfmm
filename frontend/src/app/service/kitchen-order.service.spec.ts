import { TestBed } from '@angular/core/testing';

import { KitchenOrderService } from './kitchen-order.service';

describe('KitchenOrderService', () => {
  let service: KitchenOrderService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(KitchenOrderService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});

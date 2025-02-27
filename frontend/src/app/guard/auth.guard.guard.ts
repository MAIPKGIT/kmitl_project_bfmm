import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { TokenStorageService } from '../service/token-storage.service';

@Injectable({
  providedIn: 'root',
})
export class AuthGuard implements CanActivate {
  constructor(private router: Router, private tokenStorage: TokenStorageService) {}

  canActivate(): boolean {
    const token = this.tokenStorage.getToken();
    if (token) {
      console.log('Token:', token);
      return true;
    }
    this.router.navigate(['/']);
    return false;
  }
}

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment.development';

@Injectable({
  providedIn: 'root'
})
export class LoginService {

  constructor(private http: HttpClient) {}

  login(credentials: any) {
    return this.http.post(`${environment.serviceUrl}/api/account/login`, credentials);
  }
}

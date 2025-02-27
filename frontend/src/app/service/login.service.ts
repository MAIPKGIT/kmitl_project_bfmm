import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment.development';

@Injectable({
  providedIn: 'root'
})
export class LoginService {
  private url = `${environment.serviceUrl}/api/account/login`;

  constructor(private http: HttpClient) {}

  login(credentials: any) {
    return this.http.post(this.url, credentials);
  }
}

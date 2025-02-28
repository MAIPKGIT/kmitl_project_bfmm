import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment.development';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class HistoryService {

  constructor(private http: HttpClient) { }

  getHistoryByDate(date: string) {
    let getUrl = `${environment.serviceUrl}/api/history/date/${date}`;
    return this.http.get<any>(getUrl);
  }
}

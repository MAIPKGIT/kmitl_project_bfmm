import { Component, NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { ProductComponent } from './components/pages/product/product.component';
import { LoginComponent } from './components/pages/login/login.component';
import { AuthGuard } from './guard/auth.guard.guard';
import { OrderingComponent } from './components/ordering/ordering.component';
import { KitchenOrderComponent } from './components/pages/kitchen-order/kitchen-order.component';
import { TableStatusComponent } from './components/pages/table-status/table-status.component';
import { RecipeComponent } from './components/pages/recipe/recipe.component';
import { IngredientComponent } from './components/pages/ingredient/ingredient.component';
import { WasteComponent } from './components/pages/waste/waste.component';
import { HistoryComponent } from './components/pages/history/history.component';

const routes: Routes = [
  { path: "", component: LoginComponent },
  { path: "ordering/:id/:code", component: OrderingComponent },
  { path: "kitchen-order", component: KitchenOrderComponent, canActivate: [AuthGuard] },
  { path: "recipe/:id", component: RecipeComponent, canActivate: [AuthGuard] },
  { path: "table", component: TableStatusComponent, canActivate: [AuthGuard] },
  { path: "ingredient", component: IngredientComponent, canActivate: [AuthGuard] },
  { path: "waste", component: WasteComponent, canActivate: [AuthGuard] },
  { path: "history", component: HistoryComponent, canActivate: [AuthGuard] },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }

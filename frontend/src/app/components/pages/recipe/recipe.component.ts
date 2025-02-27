import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Router } from '@angular/router';
import { RecipeService } from '../../../service/recipe.service';
import { ViewChild, ElementRef } from '@angular/core';
import Swal from 'sweetalert2';

@Component({
  selector: 'app-recipe',
  standalone: false,
  templateUrl: './recipe.component.html',
  styleUrl: './recipe.component.css'
})
export class RecipeComponent implements OnInit {
  @ViewChild('fileInput') fileInput!: ElementRef;
  menu_types: any[] = [];
  menu_by_type_id: any[] = [];
  category: any;
  selectedId: any;
  newMenu: any = { type_id: '', name: '', des: '', price: null, tag: '', warning: '' };
  selectedFile: File | null = null;
  steps: {
    isNew: boolean;
    id: any; step: number; description: string 
}[] = [];
  createdMenuId: number | null = null;
  editedMenu: any = {};

  constructor(
    private service: RecipeService,
    private route: ActivatedRoute,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.service.getAllMenuTypes().subscribe((res) => {
      this.menu_types = res;
      console.log('Menu Types:', this.menu_types);
    });

    this.route.params.subscribe(params => {
      this.selectedId = params['id'];
      console.log('Loaded ID from URL:', this.selectedId);

      if (this.selectedId) {
        this.loadMenusById(this.selectedId);
      } else {
        console.error('Category ID is undefined');
      }
    });
  }

  loadMenusById(id: any) {
    console.log('Fetching menus for category ID:', id);

    this.service.getAllMenusById(id).subscribe(
      (res) => {
        this.menu_by_type_id = res;
        console.log('Menus Loaded:', this.menu_by_type_id);
      },
      (error) => {
        console.error('Error fetching menus:', error);
      }
    );
  }

  getStepByMenuId(menu_id: number) {
    console.log('step: ', menu_id);
  }

  selectMenuTypesById(id: any) {
    let url = `/recipe/${id}`;
    console.log('Navigating to:', url);
    this.router.navigateByUrl('/', { skipLocationChange: true }).then(() => {
      this.router.navigate([url]);
    });
  }

  // ฟังก์ชันเลือกไฟล์ภาพ
  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
  }

  createMenu() {
    if (!this.newMenu.type_id || !this.newMenu.name || !this.newMenu.price || !this.selectedFile) {
        Swal.fire('Error', 'กรุณากรอกข้อมูลให้ครบถ้วน', 'error');
        return;
    }

    const menuData = {
        type_id: this.newMenu.type_id,
        name: this.newMenu.name,
        image: this.selectedFile ? this.selectedFile.name : "",
        des: this.newMenu.des ? this.newMenu.des : "",
        price: this.newMenu.price,
        tag: this.newMenu.tag ? this.newMenu.tag : "",
        warning: this.newMenu.warning ? this.newMenu.warning : ""
    };

    console.log("Sending JSON Data:", menuData);

    this.service.createMenu(menuData).subscribe(
        res => {
            console.log("Menu created successfully:", res);
            Swal.fire('Success', 'เพิ่มเมนูสำเร็จ!', 'success');
            this.loadMenusById(this.selectedId);
            this.resetForm();

            // แก้ไข: รอให้ค่าของ createdMenuId อัปเดต
            setTimeout(() => {
                this.createdMenuId = res.menu_id;
                console.log("🔹 Created menu ID:", this.createdMenuId);

                if (this.createdMenuId) {
                    this.openStepModal();
                } else {
                    console.error("Error: Menu ID is still null.");
                }
            }, 100); // รอ 100ms เพื่อให้ Angular อัปเดตค่า
        },
        error => {
            console.error("Error creating menu:", error);
            Swal.fire('Error', 'เกิดข้อผิดพลาด', 'error');
        }
    );
  }

  openStepModal() {
    const stepModalElement = document.getElementById('addStepModal');
    if (!stepModalElement) {
        console.error("Error: Step Modal element not found!");
        return;
    }

    console.log("Opening Step Modal for menu_id:", this.createdMenuId);

    const stepModal = new (window as any).bootstrap.Modal(stepModalElement);
    stepModal.show();
  }


  addStep() {
    const newStep = { id: null, step: this.steps.length + 1, description: "", isNew: true };
    this.steps.push(newStep);
  }

  removeStep(index: number) {
    this.steps.splice(index, 1);
    // อัปเดตค่า step ใหม่ให้เป็นลำดับที่ถูกต้อง
    this.steps.forEach((step, i) => step.step = i + 1);
  }

  async createSteps() {
    if (!this.createdMenuId) {
      console.error("Error: Menu ID is missing.");
      return;
    }
  
    if (this.steps.length === 0) {
      Swal.fire('Warning', 'กรุณาเพิ่มอย่างน้อย 1 ขั้นตอน', 'warning');
      return;
    }
  
    for (const stepData of this.steps) {
      const stepPayload = {
        step: stepData.step,
        menu_id: this.createdMenuId,
        description: stepData.description
      };
  
      console.log(stepPayload);
  
      try {
        const stepRes = await this.service.createStep(stepPayload).toPromise();
        console.log(stepRes);
      } catch (stepErr) {
        console.error('Error creating step:', stepErr);
      }
    }
  
    Swal.fire('Success', 'เพิ่มขั้นตอนสำเร็จ!', 'success');
  }  

  async createNewSteps() {
    if (!this.editedMenu.id) {
      console.error("Error: Menu ID is missing.");
      return;
    }
  
    // กรองเฉพาะขั้นตอนใหม่
    const newSteps = this.steps.filter(step => step.isNew);

    if (newSteps.length === 0) {
      Swal.fire('Warning', 'ไม่มีขั้นตอนใหม่ให้เพิ่ม', 'warning');
      return;
    }

    for (const stepData of newSteps) {
      const stepPayload = {
        step: stepData.step,
        menu_id: this.editedMenu.id,  // ใช้ `editedMenu.id` เพราะกำลังแก้ไขเมนู
        description: stepData.description
      };
  
      console.log(`Creating new step ${stepPayload.step}:`, stepPayload);
  
      try {
        const stepRes = await this.service.createStep(stepPayload).toPromise();
        console.log(`Step ${stepPayload.step} created successfully!`, stepRes);
      } catch (stepErr) {
        console.error('Error creating step:', stepErr);
      }
    }
  
    Swal.fire('Success', 'เพิ่มขั้นตอนใหม่สำเร็จ!', 'success');
  }

  resetForm() {
    this.newMenu = {
        type_id: '',
        name: '',
        des: '',
        price: null,
        tag: '',
        warning: ''
    };
    this.selectedFile = null;
    this.steps = [];
    this.createdMenuId = null;
  }

  onModalClose() {
    this.resetForm();
  }

  trackByFn(index: number, item: any) {
    return item.step;
  }
  
  openEditMenuModal(menu: any) {
    console.log("เปิด Modal แก้ไขเมนู:", menu);
    
    this.editedMenu = { ...menu }; 
    this.steps = []; 
    this.selectedFile = null;

    if (this.fileInput) {
      this.fileInput.nativeElement.value = "";
    }
  
    // โหลดข้อมูลเมนูจาก API (ดึงข้อมูลที่อัปเดตล่าสุด)
    this.service.getMenuById(menu.id).subscribe(
      (res) => {
        this.editedMenu = res;
        console.log("ข้อมูลเมนูที่โหลดมา:", this.editedMenu);
      },
      (error) => {
        console.error("Error fetching menu details:", error);
      }
    );

    this.service.getStepById(this.editedMenu.id).subscribe((res) => {
      console.log("Reloading updated steps:", res);
      this.steps = res.map((step: any) => ({
          id: step.id, 
          step: step.step,
          description: step.description,
          isNew: false
      }));
  });
  
    // เปิด Modal
    const editModal = new (window as any).bootstrap.Modal(document.getElementById('editMenuModal'));
    editModal.show();
  }
  
  updateMenu() {
    if (!this.editedMenu.id) {
      console.error("ไม่มี Menu ID!");
      return;
    }
  
    const updatedData: any = {
      name: this.editedMenu.name,
      des: this.editedMenu.des,
      price: this.editedMenu.price,
      tag: this.editedMenu.tag,
      warning: this.editedMenu.warning
    };

    if (this.selectedFile) {
      updatedData.image = this.selectedFile.name;
    }
  
    console.log("ส่งข้อมูลไปอัปเดตเมนู:", updatedData);
  
    this.service.updateMenu(this.editedMenu.id, updatedData).subscribe(
      (res) => {
        console.log("เมนูอัปเดตสำเร็จ!", res);
        Swal.fire("สำเร็จ", "อัปเดตเมนูเรียบร้อย!", "success");
        
        // โหลดเมนูใหม่หลังอัปเดต
        this.loadMenusById(this.selectedId);
      },
      (error) => {
        console.error("Error updating menu:", error);
        Swal.fire("เกิดข้อผิดพลาด", "ไม่สามารถอัปเดตเมนูได้", "error");
      }
    );
  }
  
  updateSteps(): void {
    if (this.steps.length === 0) {
        Swal.fire('Warning', 'ไม่มีขั้นตอนให้บันทึก', 'warning');
        return;
    }

    this.steps.filter(step => !step.isNew).forEach(step => {
        const stepId = step.id;

        if (!stepId || isNaN(Number(stepId))) {
            console.error("Error: step_id is missing or not a valid number for step:", step);
            return;
        }

        const stepPayload = {
            step: step.step,
            description: step.description,
            menu_id: this.editedMenu.id
        };

        console.log(`📤 Sending update request for Step ID ${stepId}:`, stepPayload);

        this.service.updateStep(stepId, stepPayload).subscribe(
            (res) => {
                console.log(`Step ${stepId} updated successfully`, res);
                // อัปเดต UI ให้เห็นการเปลี่ยนแปลง
                this.getStepByMenuId(this.editedMenu.id);
            },
            (error) => {
                console.error(`Error updating step ${stepId}:`, error);
                Swal.fire('Error', 'ไม่สามารถอัพเดทขั้นตอนได้', 'error');
            }
        );
    });

    Swal.fire('Success', 'บันทึกการแก้ไขขั้นตอนสำเร็จ!', 'success');
  }

}